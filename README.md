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
