import os

from mock import *
from nose.tools import *

HERE = os.path.dirname(__file__)


def fixture(*path):
    return open(fixture_path(*path), 'rb')


def fixture_path(*path):
    return os.path.join(HERE, 'fixtures', *path)
