from __future__ import unicode_literals
import datetime
import os

from tagalog import io

__all__ = ['io', 'stamp', 'tag']
__version__ = '0.1.0'

# Use UTF8 for stdin, stdout, stderr
os.environ['PYTHONIOENCODING'] = 'utf-8'


def now():
    return  _now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def stamp(iterable, key='@timestamp'):
    """
    Compute an accurate timestamp for each dict or dict-like object in
    ``iterable``, adding an accurate timestamp to each one when received. The
    timestamp is a usecond-precision ISO8601 string. The timestamp is added to
    each dict with a key set by ``key``.
    """
    for item in iterable:
        item[key] = now()
        yield item


def tag(iterable, tags=None, key='@tags'):
    """
    Add tags to each dict or dict-like object in ``iterable``. Tags are added
    to each dict with a key set by ``key``. If a key already exists under the
    key given by ``key``, this function will attempt to ``.extend()``` it, but
    will fall back to replacing it in the event of error.
    """
    if not tags:
        for item in iterable:
            yield item

    else:
        for item in iterable:
            yield _tag(item, tags, key)


def _now():
    return datetime.datetime.utcnow()


def _tag(item, tags, key):
    if item.get(key):
        try:
            item[key].extend(tags)
            return item
        except (AttributeError, TypeError):
            pass

    item[key] = tags[:]
    return item

