from __future__ import unicode_literals
from ..helpers import assert_equal, fixture, assert_in
from subprocess import Popen, PIPE

def test_happy_path_for_tagging():
    p = Popen('echo hello | logtag --no-stamp -t handbags',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate()
    assert_equal(u'{\"@message\": \"hello\", \"@tags\": [\"handbags\"]}\n', data_out)

def test_happy_path_for_single_field():
    p = Popen('echo hello | logtag --no-stamp -f handbags=great',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate()
    assert_equal(u'{\"@message\": \"hello\", \"@handbags\": \"great\"}\n', 
                 data_out)


def test_happy_path_for__multi_field():
    p = Popen('echo hello | logtag --no-stamp -f handbags=great why=because',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate()
    assert_in(u'\"@why\": \"because\"', data_out)
    assert_in(u'\"@message\": \"hello\"', data_out)
    assert_in(u'\"@handbags\": \"great\"', data_out)
    