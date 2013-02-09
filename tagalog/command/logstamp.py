from __future__ import print_function, unicode_literals
import sys

from tagalog import io, now


def main():
    for msg in io.lines(sys.stdin):
        print(now(), msg, end='')

if __name__ == '__main__':
    main()
