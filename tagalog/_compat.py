try:
    from urlparse import urlparse
except ImportError: # Python3
    from urllib import parse as urlparse

try:
    _xrange = xrange
except NameError:
    _xrange = range
