from ..helpers import assert_equal
from subprocess import Popen, PIPE, check_call
import json

def test_dry_run_for_interpretation_errors():
    p = check_call('echo hello | logship --shipper null --no-stamp -t check_tags -f ensure=checked',
              shell=True,
              stdout=PIPE,
              stdin=PIPE)