from ..helpers import *
import os
from tagalog.shipper import IShipper
from tagalog.shipper import ConnectionError, RoundRobinConnectionPool
from tagalog.shipper import register_shipper, unregister_shipper, get_shipper


class MyShipper(IShipper):
    pass


class MockConnection(object):

    def __init__(self, **kwargs):
        self.pid = os.getpid()
        self.disconnected = 0
        for k, v in kwargs.items():
            setattr(self, k, v)

    def disconnect(self):
        self.disconnected += 1


class TestRoundRobinConnectionPool(object):

    def setup(self):
        self.p = RoundRobinConnectionPool(patterns=[{'name': 'a'},
                                                    {'name': 'b'}],
                                          connection_class=MockConnection)

    def test_get_connection(self):
        a = self.p.get_connection('SET')
        b = self.p.get_connection('SET')
        c = self.p.get_connection('SET')
        assert_equal(a.name, 'a')
        assert_equal(b.name, 'b')
        assert_equal(c.name, 'a')

    def test_add_pattern(self):
        a = self.p.get_connection('SET')
        self.p.add_pattern({'name': 'c'})
        b = self.p.get_connection('SET')
        c = self.p.get_connection('SET')
        assert_equal(a.name, 'a')
        assert_equal(b.name, 'b')
        assert_equal(c.name, 'c')

    def test_remove_pattern(self):
        self.p.remove_pattern({'name': 'a'})
        a = self.p.get_connection('SET')
        b = self.p.get_connection('SET')
        assert_equal(a.name, 'b')
        assert_equal(b.name, 'b')

    def test_remove_pattern_disconnects(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'a'})
        assert_equal(a1.disconnected, 1)

    def test_remove_pattern_during_cycle_new_conn(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'a'})
        b2 = self.p.get_connection('SET')
        assert_equal(b2.name, 'b')

    def test_remove_earlier_pattern_during_cycle(self):
        a1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'a'})
        b1 = self.p.get_connection('SET')
        assert_equal(b1.name, 'b')

    def test_remove_next_pattern_during_cycle(self):
        self.p.add_pattern({'name': 'c'})
        a1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'b'})
        c1 = self.p.get_connection('SET')
        assert_equal(c1.name, 'c')

    def test_remove_next_pattern_at_end_during_cycle(self):
        self.p.add_pattern({'name': 'c'})
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'c'})
        a2 = self.p.get_connection('SET')
        assert_equal(a2.name, 'a')

    def test_remove_pattern_during_cycle_released_conn(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'a'})
        self.p.release(b1)
        b2 = self.p.get_connection('SET')
        assert_equal(b1, b2)

    def test_release(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.release(a1)
        self.p.release(b1)
        a2 = self.p.get_connection('SET')
        b2 = self.p.get_connection('SET')
        assert_equal(a1, a2)
        assert_equal(b1, b2)

    def test_purge_in_use(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.purge(a1)
        self.p.release(b1)
        a2 = self.p.get_connection('SET')
        b2 = self.p.get_connection('SET')
        assert_not_equal(a1, a2)
        assert_equal(b1, b2)
        assert_equal(a1.disconnected, 1)

    def test_purge_released(self):
        a1 = self.p.get_connection('SET')
        self.p.release(a1)
        self.p.purge(a1)
        self.p.get_connection('SET') # skip one
        a2 = self.p.get_connection('SET')
        assert_not_equal(a1, a2)
        assert_equal(a1.disconnected, 1)

    def test_disconnect(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.release(a1)
        self.p.release(b1)
        a2 = self.p.get_connection('SET')
        b2 = self.p.get_connection('SET')
        self.p.disconnect()
        assert_equal(a1.disconnected, 1)
        assert_equal(b1.disconnected, 1)
        assert_equal(a2.disconnected, 1)
        assert_equal(b2.disconnected, 1)

    def test_too_many_connections(self):
        p = RoundRobinConnectionPool(patterns=[{'name': 'a'},
                                               {'name': 'b'}],
                                     connection_class=MockConnection,
                                     max_connections_per_pattern=1)
        p.get_connection('SET')
        p.get_connection('SET')
        assert_raises(ConnectionError, p.get_connection, 'SET')


def test_shipper_registration():
    register_shipper('myshipper', MyShipper)
    assert_equal(get_shipper('myshipper'), MyShipper)
    unregister_shipper('myshipper')
    assert_equal(get_shipper('myshipper'), None)


def test_shipper_cant_reregister():
    register_shipper('myshipper', MyShipper)
    assert_raises(RuntimeError, register_shipper, 'myshipper', MyShipper)
    unregister_shipper('myshipper')

