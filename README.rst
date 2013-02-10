Tagalog
=======

A set of commandline tools for manipulating logfiles on the fly.

.. image:: https://travis-ci.org/nickstenning/tagalog.png?branch=master
   :target: https://travis-ci.org/nickstenning/tagalog

Installation
------------

Tagalog is available on PyPI_ and can be installed using pip_::

    $ pip install tagalog

.. _PyPI: http://pypi.python.org/pypi
.. _pip: http://www.pip-installer.org/

Usage
-----

Tagalog consists of a number of simple commandline utilities which help you do
things to logging data. Most of these tools assumes that it will receive log
data on STDIN, and emits some transformed log data on STDOUT.

The simplest tool in Tagalog is ``logstamp``, which simply prefixes each line
it receives with a precise timestamp::

    $ seq 3 | logstamp
    2013-02-09T18:52:57.893966Z 1
    2013-02-09T18:52:57.894272Z 2
    2013-02-09T18:52:57.894316Z 3

Of course, you're probably not going find much use for ``logstamp`` if all you
do is pipe ``seq 3`` into it. Instead, use it to timestamp your application
logs::

    $ ruby myapp.rb | logstamp >app.log

Next up is ``logtag``, which transforms each log line into a
Logstash_-compatible JSON document. In addition to adding a ``@timestamp``
field, you can also add a list of tags to each document::

    $ seq 3 | logtag -t "$(hostname -f)" sequence
    {"@timestamp": "2013-02-09T19:02:05.200903Z", "@message": "1", "@tags": ["ravel.local", "sequence"]}
    {"@timestamp": "2013-02-09T19:02:05.201349Z", "@message": "2", "@tags": ["ravel.local", "sequence"]}
    {"@timestamp": "2013-02-09T19:02:05.201398Z", "@message": "3", "@tags": ["ravel.local", "sequence"]}

.. _Logstash: http://logstash.net/

Probably the most useful tool in the box, however, is ``logship``, which does
everything ``logtag`` does, but instead of simply printing the log data to
STDOUT, it ships it somewhere else. In the future, I expect logship to be able
to send logging data to a number of different kinds of destination. At the
moment, it will connect to one or more Redis servers and will ``LPUSH`` the
logs onto a Redis list key of your choice.::

    $ ruby myapp.rb | logship -k mylogs -u redis://redis-1.internal:7777 redis://redis-2.internal:7778 redis://redis-3.internal:7779

Do ``logship -h`` to see available options.

**NB**: ``logship`` is intended to be robust against failure of the log
recipients. If it fails to submit a log entry to one of the redis servers in
its list, it will try the next one. If it cannot connect to any of them, it
will print a warning to STDERR but will otherwise carry on as normal. In the
event that it cannot submit to any server, it will simply drop the log entries
to avoid building up a backlog that could later result in a `thundering
herd`_.

.. _thundering herd: http://en.wikipedia.org/wiki/Thundering_herd_problem

Lastly, there is ``logtext``, which does roughly the reverse of ``logtag``. It
reads JSON documents on STDIN and translates them back into plain text::

    $ seq 3 | logtag -t "$(hostname -f)" sequence --no-stamp | logtext
    1
    2
    3

License
-------

Tagalog is released under the MIT license, a copy of which can be found in
``LICENSE``.

