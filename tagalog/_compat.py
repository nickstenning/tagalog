try:
    from urlparse import urlparse
except ImportError: # Python3
    from urllib.parse import urlparse

try:
    _xrange = xrange
except NameError:
    _xrange = range
