import os
from itertools import chain
import logging

from redis import Connection, ConnectionError, StrictRedis

from tagalog._compat import urlparse, _xrange


log = logging.getLogger(__name__)

SHIPPERS = {}


class ShipperError(Exception):
    pass


class IShipper(object):
    """
    Abstract class representing a log shipper. Log shippers should implement
    the following methods:
    """

    def __init__(self, args):
        self.args = args

    def ship(self, message):
        raise NotImplementedError('IShipper subclasses should implement the "ship" method!')


class RoundRobinConnectionPool(object):
    """
    Round-robin Redis connection pool
    """
    def __init__(self,
                 patterns=None,
                 max_connections_per_pattern=None,
                 connection_class=Connection):
        self.patterns = []
        self.num_patterns = 0
        self.pid = os.getpid()
        self.connection_class = connection_class
        self.max_connections_per_pattern = max_connections_per_pattern or 2 ** 31
        self._pattern_idx = 0
        self._created_connections = []
        self._available_connections = []
        self._in_use_connections = []

        if patterns is not None:
            for patt in patterns:
                self.add_pattern(patt)

    def _checkpid(self):
        if self.pid != os.getpid():
            self.disconnect()
            self.__init__(self.patterns,
                          self.max_connections_per_pattern,
                          self.connection_class)

    def _next_pattern(self):
        self._pattern_idx = (self._pattern_idx + 1) % self.num_patterns

    def add_pattern(self, pattern):
        self.patterns.append(pattern)
        self.num_patterns += 1
        self._created_connections.append(0)
        self._available_connections.append([])
        self._in_use_connections.append(set())

    def remove_pattern(self, pattern):
        idx = self.patterns.index(pattern)
        self.patterns.pop(idx)

        # Keep the pattern index pointing at the correct pattern
        if idx < self._pattern_idx:
            self._pattern_idx -= 1

        # Disconnect connections for the removed pattern
        conns = chain(self._available_connections[idx],
                      self._in_use_connections[idx])
        for conn in conns:
            conn.disconnect()

        # Relabel all remaining connections
        for c in self.all_connections():
            if c._pattern_idx > idx:
                c._pattern_idx -= 1

        self._created_connections.pop(idx)
        self._available_connections.pop(idx)
        self._in_use_connections.pop(idx)
        self.num_patterns -= 1

        # Final adjustment to the pattern index to ensure we're not pointing
        # past the end of the pattern list
        if self._pattern_idx > self.num_patterns - 1:
            self._pattern_idx = 0

    def all_connections(self):
        """Returns a generator over all current connection objects"""
        for i in _xrange(self.num_patterns):
            for c in self._available_connections[i]:
                yield c
            for c in self._in_use_connections[i]:
                yield c

    def get_connection(self, command_name, *keys, **options):
        """Get a connection from the pool"""
        self._checkpid()
        try:
            connection = self._available_connections[self._pattern_idx].pop()
        except IndexError:
            connection = self.make_connection()
        self._in_use_connections[self._pattern_idx].add(connection)
        self._next_pattern()
        return connection

    def make_connection(self):
        """Create a new connection"""
        if self._created_connections[self._pattern_idx] >= self.max_connections_per_pattern:
            raise ConnectionError("Too many connections")
        self._created_connections[self._pattern_idx] += 1
        conn = self.connection_class(**self.patterns[self._pattern_idx])
        conn._pattern_idx = self._pattern_idx
        return conn

    def release(self, connection):
        """Releases the connection back to the pool"""
        self._checkpid()
        if connection.pid == self.pid:
            idx = connection._pattern_idx
            self._in_use_connections[idx].remove(connection)
            self._available_connections[idx].append(connection)

    def purge(self, connection):
        """Remove the connection from rotation"""
        self._checkpid()
        if connection.pid == self.pid:
            idx = connection._pattern_idx
            if connection in self._in_use_connections[idx]:
                self._in_use_connections[idx].remove(connection)
            else:
                self._available_connections[idx].remove(connection)
            connection.disconnect()

    def disconnect(self):
        """Disconnect all connections in the pool"""
        for conn in self.all_connections():
            conn.disconnect()

class ResilientStrictRedis(StrictRedis):

    @property
    def execution_attempts(self):
        if not hasattr(self, '_execution_attempts'):
            self._execution_attempts = 1
        return self._execution_attempts

    @execution_attempts.setter
    def execution_attempts(self, num):
        self._execution_attempts = num

    def execute_command(self, *args, **options):
        """Execute a command and return a parsed response"""
        pool = self.connection_pool
        command_name = args[0]
        for i in _xrange(self.execution_attempts):
            connection = pool.get_connection(command_name, **options)
            try:
                connection.send_command(*args)
                res = self.parse_response(connection, command_name, **options)
                pool.release(connection)
                return res
            except ConnectionError:
                pool.purge(connection)
                if i >= self.execution_attempts - 1:
                    raise


class RedisShipper(IShipper):

    def __init__(self, args):
        self.args = args
        self.key = args.key

        patts = [self._parse_url(u) for u in args.urls]
        self.pool = RoundRobinConnectionPool(patterns=patts)
        self.rc = ResilientStrictRedis(connection_pool=self.pool)
        self.rc.execution_attempts = self.pool.num_patterns

    def ship(self, msg):
        try:
            self.rc.lpush(self.key, msg)
        except ConnectionError as e:
            log.warn('Could not ship message: {0}'.format(e))

    def _parse_url(self, url):
        parsed = urlparse(url)
        db = 0

        if parsed.path.startswith('/'):
            path = parsed.path[1:]
        else:
            path = parsed.path

        if path:
            try:
                db = int(path)
            except ValueError:
                msg = 'Could not parse "{0}" as a valid Redis DB number!'.format(path)
                raise ValueError(msg)

        return {'host': parsed.hostname or 'localhost',
                'port': parsed.port or 6379,
                'db': db}


class NullShipper(IShipper):

    def ship(self, msg):
        pass


def register_shipper(name, constructor):
    if name not in SHIPPERS:
        SHIPPERS[name] = constructor
    else:
        raise RuntimeError('Shipper "{0}" already defined!'.format(name))


def unregister_shipper(name):
    return SHIPPERS.pop(name, None)


def get_shipper(name):
    return SHIPPERS.get(name)

register_shipper('redis', RedisShipper)
register_shipper('null', NullShipper)
