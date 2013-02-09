from __future__ import print_function, unicode_literals
import json
import sys

from tagalog import io

def main():
    for line in io.lines(sys.stdin):
        msg = json.loads(line)
        if '@timestamp' in msg:
            print(msg['@timestamp'], msg['@message'])
        else:
            print(msg['@message'])

if __name__ == '__main__':
    main()
