# REVIEW — Video phase (tcf-chamber-media · `video-phase`)

This is the review pack for Opus. Every file is new, so each one is shown in full.

## `.github/workflows/compress-videos.yml`

```yaml
# ═══════════════════════════════════════════════════════════
# tcf-chamber-media · Compress chamber videos (manual only)
# 1. Reads the list of chamber videos from tcf-chamber's chambers.json.
# 2. Downloads each original from the main TCF site (public URL).
#    Originals stay in the-Civilisation-field; nothing there changes.
# 3. Re-encodes with the tested settings:
#    H.264 libx264 preset slow, max 720p (shorter side), CRF 26,
#    AAC 96k, +faststart, yuv420p. Same file names, into videos/.
# 4. Stops if the compressed total is over 900 MB.
# 5. Commits videos/ to main, deploys GitHub Pages, and checks that
#    every video URL is reachable.
# Files already in videos/ are skipped unless "force" is chosen.
# ═══════════════════════════════════════════════════════════
name: Compress chamber videos

on:
  workflow_dispatch:
    inputs:
      force:
        description: "Re-encode videos that already exist in videos/"
        type: boolean
        default: false

permissions:
  contents: write
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

env:
  ORIGINALS: https://chinsookling.github.io/the-Civilisation-field/assets/videos/

jobs:
  compress:
    runs-on: ubuntu-latest
    timeout-minutes: 300
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install ffmpeg
        run: sudo apt-get update && sudo apt-get install -y ffmpeg

      - name: Compress
        env:
          FORCE: ${{ inputs.force }}
        run: |
          set -euo pipefail
          mkdir -p videos _orig
          python3 tools/video_list.py > _list.txt
          echo "videos listed: $(wc -l < _list.txt)"
          echo "| File | Original | Compressed |" > _sizes.md
          echo "|---|---|---|" >> _sizes.md
          orig_total=0
          while IFS= read -r f; do
            if [ -s "videos/$f" ] && [ "$FORCE" != "true" ]; then echo "skip $f"; continue; fi
            url="$ORIGINALS$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$f")"
            curl -fsSL --retry 3 -o "_orig/$f" "$url"
            ffmpeg -nostdin -loglevel error -y -i "_orig/$f" \
              -c:v libx264 -preset slow -crf 26 \
              -vf "scale='if(gte(iw,ih),-2,min(720,iw))':'if(gte(iw,ih),min(720,ih),-2)'" \
              -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart \
              "videos/$f"
            o=$(stat -c%s "_orig/$f"); n=$(stat -c%s "videos/$f")
            orig_total=$((orig_total + o))
            echo "| $f | $o | $n |" >> _sizes.md
            rm -f "_orig/$f"
          done < _list.txt
          new_total=$(du -sb videos | cut -f1)
          echo "ORIGINAL bytes (this run): $orig_total"
          echo "COMPRESSED bytes (videos/ total): $new_total"
          {
            echo "## Compression result"
            echo ""
            echo "- Original (encoded in this run): $orig_total bytes"
            echo "- Compressed total in videos/: $new_total bytes"
            echo ""
            cat _sizes.md
          } >> "$GITHUB_STEP_SUMMARY"
          if [ "$new_total" -gt 943718400 ]; then
            echo "::error::Compressed total is over 900 MB. Stopping without committing."
            exit 1
          fi
          rm -rf _orig _list.txt _sizes.md

      - name: Commit videos to main
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898183+github-actions[bot]@users.noreply.github.com"
          git add videos
          if git diff --cached --quiet; then echo "nothing new to commit"; exit 0; fi
          git commit -m "Compressed chamber videos (720p, CRF 26, AAC 96k)"
          git push origin HEAD:main

  deploy:
    needs: compress
    uses: ./.github/workflows/deploy-pages.yml
```

## `.github/workflows/deploy-pages.yml`

```yaml
# ═══════════════════════════════════════════════════════════
# tcf-chamber-media · Deploy GitHub Pages, then check every video URL
# Runs on push to main, by hand, or after "Compress chamber videos".
# Excludes docs/architecture/ and *.bak* (same approach as the other
# TCF repos).
# ═══════════════════════════════════════════════════════════
name: Deploy Pages

on:
  push:
    branches: [main]
  workflow_dispatch:
  workflow_call:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout main
        uses: actions/checkout@v4
        with:
          ref: main

      - name: Build curated site
        run: |
          mkdir -p _site
          rsync -a \
            --exclude='.git/' --exclude='.github/' --exclude='_site/' \
            --exclude='docs/architecture/' --exclude='*.bak*' \
            ./ _site/
          touch _site/.nojekyll
          echo "videos: $(ls _site/videos 2>/dev/null | wc -l) files, $(du -sh _site/videos 2>/dev/null | cut -f1)"

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: _site

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4

  check:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - name: Checkout main
        uses: actions/checkout@v4
        with:
          ref: main
      - name: Check every video URL
        run: |
          if [ ! -d videos ] || [ -z "$(ls videos)" ]; then echo "no videos yet; skipping check"; exit 0; fi
          sleep 30
          python3 tools/check_urls.py | tee -a "$GITHUB_STEP_SUMMARY"
```

## `tools/video_list.py`

```python
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
```

## `tools/check_urls.py`

```python
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
```

## `README.md`

```markdown
# tcf-chamber-media

Compressed videos for **The Chamber** (畫) of The Civilisation Field.

- **Served at:** https://chinsookling.github.io/tcf-chamber-media/videos/
- **Used by:** https://chinsookling.github.io/tcf-chamber/ through `media_base` in tcf-chamber's `docs/data/chambers.json`
- **Main TCF site:** https://chinsookling.github.io/the-Civilisation-field/

This site follows docs/standards/AI-READABLE-STANDARD-v0.4.md in the main TCF repo.

## What is here

`videos/` holds one compressed copy of every chamber video, with the **same file names** as the originals.

## Settings (tested and approved by Tuzi)

H.264 (libx264, preset slow), max 720p (the shorter side is capped at 720, and the aspect ratio is kept), CRF 26, AAC 96 kbps, `+faststart`, yuv420p.

## Originals

The original high-quality videos are kept in `the-Civilisation-field` (`assets/videos/`). **Nothing in this repo replaces or deletes them.**

## How videos get here

The workflow **Compress chamber videos** (Actions → Run workflow) does the following:

1. Reads the video list from tcf-chamber's `chambers.json`.
2. Downloads each original from the main site.
3. Compresses it with the settings above.
4. Commits the result to `videos/`.
5. Deploys this site and checks that every video URL works.

Files already in `videos/` are skipped, so after adding a new chamber you only need to run it once more.

## License

Original content is licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). AI and guest responses are preserved as records; their rights depend on each case.
```

## `index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chamber media · The Civilisation Field</title>
<meta name="description" content="Compressed videos for The Chamber (畫) of The Civilisation Field.">
</head>
<body style="margin:0;padding:24px 16px;background:#06080f;color:#e8e8f0;font:16px/1.6 Georgia,serif">
<main style="max-width:42rem;margin:0 auto">
<h1>Chamber media</h1>
<p>This site holds the compressed videos for The Chamber (畫) of The Civilisation Field. They are used by the chamber pages; there is nothing to browse here.</p>
<ul>
  <li><a style="color:#d4b978" href="https://chinsookling.github.io/tcf-chamber/">The Chamber</a></li>
  <li><a style="color:#d4b978" href="https://chinsookling.github.io/tcf-chamber/chambers/">Every chamber as text</a></li>
  <li><a style="color:#d4b978" href="https://chinsookling.github.io/the-Civilisation-field/">The Civilisation Field</a></li>
</ul>
<p>Original content is licensed under CC BY 4.0. Reading is not permission to act.</p>
</main>
</body>
</html>
```

## Local dry run of the Compress step (2 files, served from a local copy of the originals)

```
videos listed: 2
ORIGINAL bytes (this run): 12243104
COMPRESSED bytes (videos/ total): 3052718

| File | Original | Compressed |
|---|---|---|
| ch001-crystal-chamber.mp4 | 3756236 | 1185377 |
| ch045-tuzi's-dream-chamber.mp4 | 8486868 | 1867341 |
```

## `check_urls.py` test (local server, ch002 left out on purpose)

```
checked 3 video URLs, missing 1
MISSING ch002-harbor-chamber.mp4
exit 1
```
