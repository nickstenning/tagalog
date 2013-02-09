#!/bin/bash
set -eux

cd "$(dirname "$0")"

if [ ! -e 1g.txt ]; then 
  bunzip2 -k 1g.txt.bz2
fi

mkdir -p data
DATE=$(date "+%Y-%m-%dT%H:%M:%S")

<1g.txt logtag --no-stamp | 
pipebench >/dev/null 2> >(tee "data/${DATE}.nostamp.bench" >&2)

<1g.txt logtag | 
pipebench >/dev/null 2> >(tee "data/${DATE}.stamp.bench" >&2)

<1g.txt logtag -t foo bar baz |
pipebench >/dev/null 2> >(tee "data/${DATE}.3tags.bench" >&2)

