import logging
from os import environ as env

from . import logship
from . import logstamp
from . import logtag
from . import logtext

__all__ = ['logship', 'logstamp', 'logtag', 'logtext']

_log_level_default = logging.INFO
_log_level = getattr(logging, env.get('TAGALOG_LOGLEVEL', '').upper(), _log_level_default)

logging.basicConfig(format='%(levelname)s: %(message)s', level=_log_level)
