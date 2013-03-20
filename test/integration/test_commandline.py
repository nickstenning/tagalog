from ..helpers import assert_equal
from subprocess import Popen, PIPE
import json

def test_tagging():
    p = Popen('echo hello | logtag --no-stamp -t handbags',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate()
    assert_equal({'@message': 'hello', '@tags': ['handbags']},
                 json.loads(data_out.decode("utf-8")))

def test_single_field():
    p = Popen('echo hello | logtag --no-stamp -f handbags=great',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate()
    assert_equal({'@message': 'hello', '@fields': { 'handbags': 'great'}},
                 json.loads(data_out.decode("utf-8")))

def test_multiple_fields():
    p = Popen('echo hello | logtag --no-stamp -f handbags=great why=because',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)
    data_out, _ = p.communicate()
    assert_equal({'@message': 'hello', '@fields': { 'handbags': 'great', 'why': 'because'}},
                 json.loads(data_out.decode("utf-8")))