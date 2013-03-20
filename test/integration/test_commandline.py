from __future__ import unicode_literals
from ..helpers import assert_equal, fixture, assert_true, assert_in
from subprocess import Popen, PIPE


def test_happy_path_for_tagging():
    p = Popen('echo hello | logtag --no-stamp -t handbags',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate()
    assert_equal('{\"@message\": \"hello\", \"@tags\": [\"handbags\"]}\n',
                 data_out.decode("utf-8"))

def test_happy_path_for_single_field():
    p = Popen('echo hello | logtag --no-stamp -f handbags=great',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate()
    assert_equal('{\"@message\": \"hello\", \"@handbags\": \"great\"}\n',
                 data_out.decode("utf-8"))


def test_happy_path_for__multi_field():
    p = Popen('echo hello | logtag --no-stamp -f handbags=great why=because',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate()
    assert_in('\"@why\": \"because\"', data_out.decode("utf-8"))
    assert_in('\"@message\": \"hello\"', data_out.decode("utf-8"))
    assert_in('\"@handbags\": \"great\"', data_out.decode("utf-8"))