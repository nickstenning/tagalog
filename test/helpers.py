import os

from mock import *
from nose.tools import *

"""
Overriding assert_in for the case where we are pre 2.7
"""
try:
  from nose.tools import assert_in
except ImportError:
  def assert_in(a, b):
    assert_true(a in b)

HERE = os.path.dirname(__file__)


def fixture(*path):
    return open(fixture_path(*path), 'rb')


def fixture_path(*path):
    return os.path.join(HERE, 'fixtures', *path)
