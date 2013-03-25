from __future__ import unicode_literals
import datetime
import os

from tagalog import io

__all__ = ['io', 'stamp', 'tag', 'fields']
__version__ = '0.2.4'

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

def fields(iterable, fields=None):
    """
    Add a set of fields to each item in ``iterable``. The set of fields have a
    key=value format. '@' are added to the front of each key.
    """
    if not fields:
        for item in iterable:
            yield item

    prepared_fields = _prepare_fields(fields)

    for item in iterable:
        yield _process_fields(item, prepared_fields)


def _process_fields(item, fields):
    item.update(fields)
    return item

def _prepare_fields(fields):
    prepared_fields = {}

    for field in fields:
        split_field = field.split('=', 1)
        if len(split_field) > 1:
          prepared_fields[split_field[0]] = split_field[1][:]
    return { '@fields': prepared_fields }


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

