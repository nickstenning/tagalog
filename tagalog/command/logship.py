from __future__ import print_function, unicode_literals
import argparse
import json
import sys
import textwrap

from tagalog import io, stamp, tag
from tagalog import shipper

parser = argparse.ArgumentParser(description=textwrap.dedent("""
    Ship log data from STDIN to somewhere else, timestamping and preprocessing
    each log entry into a JSON document along the way."""))
parser.add_argument('-t', '--tags', nargs='+')
parser.add_argument('-s', '--shipper', default='redis')
parser.add_argument('-k', '--key', default='logs')
parser.add_argument('-u', '--urls', nargs='+', default=['redis://localhost:6379'])
parser.add_argument('--no-stamp', action='store_true')

def main():
    args = parser.parse_args()
    shpr = shipper.get_shipper(args.shipper)(args)

    msgs = io.messages(sys.stdin)
    if not args.no_stamp:
        msgs = stamp(msgs)
    if args.tags:
        msgs = tag(msgs, args.tags)
    for msg in msgs:
        shpr.ship(json.dumps(msg))

if __name__ == '__main__':
    main()
