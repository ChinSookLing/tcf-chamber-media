#!/usr/bin/env python3
"""
List the chamber video file names that tcf-chamber uses.

Reads tcf-chamber's docs/data/chambers.json (the single source of truth for
chambers) and prints each video file name once, in chamber order.

    python3 tools/video_list.py                 # from GitHub (tcf-chamber main)
    python3 tools/video_list.py path/to/chambers.json
"""
import json
import sys
import urllib.request

SOURCE = 'https://raw.githubusercontent.com/ChinSookLing/tcf-chamber/main/docs/data/chambers.json'


def load(src):
    if src.startswith('http'):
        with urllib.request.urlopen(src, timeout=60) as r:
            return json.loads(r.read().decode('utf-8'))
    with open(src, encoding='utf-8') as f:
        return json.load(f)


def names(data):
    chambers = data if isinstance(data, list) else data['chambers']
    out = []
    for c in chambers:
        v = c.get('video')
        for p in (v if isinstance(v, list) else [v] if v else []):
            n = str(p).split('/')[-1]
            if n not in out:
                out.append(n)
    return out


if __name__ == '__main__':
    print('\n'.join(names(load(sys.argv[1] if len(sys.argv) > 1 else SOURCE))))
