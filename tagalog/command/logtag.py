from __future__ import print_function, unicode_literals
import argparse
import json
import sys
import textwrap

from tagalog import io, stamp, tag, fields

parser = argparse.ArgumentParser(description=textwrap.dedent("""
    Convert log data on STDIN to a stream of timestamped JSON documents on STDOUT,
    optionally adding tags and data fields to the processed log lines."""))
parser.add_argument('-t', '--tags', nargs='+')
parser.add_argument('-f', '--fields', nargs='+',
                    help='Add key=value fields specified to each request')
parser.add_argument('--no-stamp', action='store_true')


def main():
    args = parser.parse_args()
    msgs = io.messages(sys.stdin)
    if not args.no_stamp:
        msgs = stamp(msgs)
    if args.tags:
        msgs = tag(msgs, args.tags)
    if args.fields:
        msgs = fields(msgs, args.fields)
    for msg in msgs:
        print(json.dumps(msg))

if __name__ == '__main__':
    main()
