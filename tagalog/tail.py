from __future__ import print_function, unicode_literals

import errno
import os
import time
import sys

try:
    from queue import Queue, Empty # Python 3
except ImportError:
    from Queue import Queue, Empty

from watchdog.events import (FileSystemEventHandler, EVENT_TYPE_MODIFIED,
                             EVENT_TYPE_MOVED, EVENT_TYPE_CREATED,
                             EVENT_TYPE_DELETED)
from watchdog.observers import Observer


def safe_open(fname, *args, **kwargs):
    try:
        return open(fname, *args, **kwargs)
    except IOError as e:
        if e.errno == errno.ENOENT:
            return None
        raise

class FileWatcherError(Exception):
    pass

class FileWatcher(object):
    """
    Watch a file for added lines and append those lines to a passed queue
    object.
    """

    def __init__(self, filename, queue):
        self.filename = os.path.abspath(filename)
        self.queue = queue
        self.fp = safe_open(self.filename)
        if self.fp:
            self.seek_to_end()

    def seek_to_end(self):
        self.fp.seek(0, os.SEEK_END)

    def push_pending(self):
        for line in self.fp.readlines():
            self.queue.put((self.filename, line))

    def dispatch(self, event):
        if event.is_directory:
            return
        if event.event_type == EVENT_TYPE_MOVED:
            if event.dest_path != self.filename:
                return
        else:
            if event.src_path != self.filename:
                return

        _method_map = {
            EVENT_TYPE_MODIFIED: self._on_modified,
            EVENT_TYPE_MOVED:    self._on_moved,
            EVENT_TYPE_CREATED:  self._on_created,
            EVENT_TYPE_DELETED:  self._on_deleted,
        }
        _method_map[event.event_type]()

    def _on_modified(self):
        """Handle the modification of an already-opened file"""
        if not self.fp:
            self.fp = safe_open(self.filename)
        if self.fp:
            self.push_pending()
            self.seek_to_end()

    def _on_created(self):
        """Handle the creation of the watched file"""
        self._close()
        self.fp = safe_open(self.filename)
        if self.fp:
            self.push_pending()
            self.seek_to_end()

    def _on_deleted(self):
        """Handle the deletion of the watched file"""
        self._close()
        self.fp = None

    def _on_moved(self):
        """Handle a file being moved into the location we're monitoring"""
        # NB: Watchdog doesn't appear to correctly handle file moves yet, so
        # if you're expecting this log file to be logrotated, make sure
        # logrotate uses the "copytruncate" method of rotating logfile.
        self._close()
        self.fp = safe_open(self.filename)
        self.seek_to_end()

    def _close(self):
        try:
            self.fp.close()
        except AttributeError:
            pass


def tail(files):
    """
    Tail a list of files. Returns a generator yielding (filename, line) tuples.
    """
    observer = Observer(timeout=0.1)
    queue = Queue()

    for f in files:
        d = os.path.dirname(f)
        observer.schedule(FileWatcher(f, queue), path=d)

    observer.start()

    while True:
        try:
            fname, line = queue.get(timeout=1)
        except Empty:
            pass
        except KeyboardInterrupt:
            observer.stop()
            break
        else:
            yield fname, line

    observer.join()


def main():
    files = sys.argv[1:]

    if not files:
        print("No files given.")
        sys.exit(1)

    for fname, line in tail(sys.argv[1:]):
        print(fname + ': ' + line, end="")


if __name__ == '__main__':
    main()
