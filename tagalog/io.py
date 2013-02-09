from __future__ import unicode_literals
import os
import sys

UTF8 = 'UTF-8'

BUF_DEFAULT = -1
BUF_UNBUFFERED = 0
BUF_LINEBUFFERED = 1


def messages(fp, key='@message'):
    """
    Read lines of UTF-8 from the file-like object given in ``fp``, with the
    same fault-tolerance as :function:`tagalog.io.lines`, but instead yield
    dicts with the line data stored in the key given by ``key`` (default:
    "@message").
    """
    for line in lines(fp):
        txt = line.rstrip('\n')
        yield {key: txt}


def lines(fp):
    """
    Read lines of UTF-8 from the file-like object given in ``fp``, making sure
    that when reading from STDIN, reads are at most line-buffered.

    UTF-8 decoding errors are handled silently. Invalid characters are
    replaced by U+FFFD REPLACEMENT CHARACTER.

    Line endings are normalised to newlines by Python's universal newlines
    feature.

    Returns an iterator yielding lines.
    """
    if fp.fileno() == sys.stdin.fileno():
        close = True

        try: # Python 3
            fp = open(fp.fileno(), mode='r', buffering=BUF_LINEBUFFERED, errors='replace')
            decode = False
        except TypeError:
            fp = os.fdopen(fp.fileno(), 'rU', BUF_LINEBUFFERED)
            decode = True

    else:
        close = False

        try:
            # only decode if the fp doesn't already have an encoding
            decode = (fp.encoding != UTF8)
        except AttributeError:
            # fp has been opened in binary mode
            decode = True

    try:
        while 1:
            l = fp.readline()
            if l:
                if decode:
                    l = l.decode(UTF8, 'replace')
                yield l
            else:
                break
    finally:
        if close:
            fp.close()

