#!/usr/bin/env python3
"""
Check that every chamber video is reachable on the published media site.

    python3 tools/check_urls.py [BASE_URL]

BASE_URL defaults to https://chinsookling.github.io/tcf-chamber-media/videos/
Exits with status 1 if any video is missing.
"""
import sys
import urllib.parse
import urllib.request

from video_list import SOURCE, load, names

BASE = 'https://chinsookling.github.io/tcf-chamber-media/videos/'


def main(base):
    missing = []
    files = names(load(SOURCE))
    for n in files:
        url = base + urllib.parse.quote(n)
        req = urllib.request.Request(url, method='HEAD')
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                ok = r.status == 200
        except Exception:
            ok = False
        if not ok:
            missing.append(n)
    print('checked %d video URLs, missing %d' % (len(files), len(missing)))
    for n in missing:
        print('MISSING ' + n)
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else BASE))
