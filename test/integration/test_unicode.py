from __future__ import unicode_literals
from ..helpers import assert_equal, fixture
from subprocess import Popen, PIPE

def test_unicode():
    data_in = fixture('utf8-demo.txt').read()

    p = Popen('logtag --no-stamp | logtext',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate(data_in)

    assert_equal(data_in, data_out)


def test_broken_unicode():
    data_in = fixture('utf8-test.txt').read()

    p = Popen('logtag --no-stamp | logtext',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate(data_in)

    test_line = data_out.splitlines()[105]
    assert_equal(test_line.decode('utf8'),
                 '3.1.4  3 continuation bytes: "\ufffd\ufffd\ufffd"                                            |')
