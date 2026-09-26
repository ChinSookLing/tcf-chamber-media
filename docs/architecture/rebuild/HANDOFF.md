# HANDOFF — Video phase (tcf-chamber-media)

- **Phase:** Video phase: compress all chamber videos into a separate media site
- **Repo / branch:** `tcf-chamber-media` · `video-phase`, from `main` @ `d9787b8` (Initial commit)
- **Related:**
  - `the-Civilisation-field` · `video-phase`: removes the compression test files.
  - `tcf-chamber`: the `media_base` switch comes **later**, after this site is live and every URL is confirmed.
- **Current owner:** Claude Code → next: Opus review → Tuzi merges → Tuzi runs "Compress chamber videos"

## What changed

| File | What |
|---|---|
| `.github/workflows/compress-videos.yml` | **Manual only.** Reads the video list from tcf-chamber's `chambers.json` (159 files; the 3 unused videos are not listed there) and downloads each original from the public main site. It re-encodes with **exactly the tested settings**, keeps the same file names, and writes to `videos/`. It **fails without committing if the total is over 900 MB**. Otherwise it commits `videos/` to `main`, then runs the deploy workflow (Pages + URL check). Files already in `videos/` are skipped unless `force` is ticked. |
| `.github/workflows/deploy-pages.yml` | Deploys GitHub Pages on push to `main`, when run by hand, or when called by the compress workflow. It excludes `docs/architecture/` and `*.bak*`. After deploying, it checks **every** video URL, and the run turns red if any is missing. |
| `tools/video_list.py` | Lists the chamber video file names from tcf-chamber's `chambers.json`, the single source of truth. |
| `tools/check_urls.py` | Checks that each video URL on the media site returns 200. |
| `README.md` | What this repo is, the settings used, where the originals are kept, how videos get here, and the license. |
| `index.html`, `.nojekyll` | A tiny landing page, so the site root is not a 404. |

**Settings** (the same as the approved test): H.264 libx264 preset slow, max 720p (the shorter side is capped at 720), CRF 26, AAC 96k, `+faststart`, yuv420p.

**Why it downloads from the public site:** `the-Civilisation-field` is a private repo, so a workflow in this repo cannot read it without an extra secret token. The same original files are published at `https://chinsookling.github.io/the-Civilisation-field/assets/videos/`. That source is only **read**, never changed.

**Why one workflow does everything:** a commit pushed by a workflow does not start other workflows. So the compress workflow calls the deploy workflow itself. You get one button: compress → commit → publish → check.

## Size report

- **Before:** 159 original videos, 1,328.8 MB (from the Phase 4 Step 0 report).
- **After:** **243.6 MB, 18% of the original** (sandbox run of all 159, below). The workflow reports its own numbers in the run **Summary**. The ffmpeg version on the runner may differ slightly, so expect a result close to this, well under the 900 MB stop.

## How to run it (for Tuzi, in this order)

1. **Merge** this PR (`video-phase` → `main`).
2. **Check that Pages uses Actions:** Settings → Pages → Build and deployment → Source = **GitHub Actions** (you have already done this).
3. **Allow the workflow to write:** Settings → Actions → General → **Workflow permissions** → choose **Read and write permissions** → **Save**. If it is left read-only, the "Commit videos to main" step fails.
4. **Run it:** go to https://github.com/ChinSookLing/tcf-chamber-media/actions, click **Compress chamber videos** on the left, then **Run workflow** → branch `main` → leave `force` unticked → **Run workflow**.
5. **Wait:** it should take about 30–90 minutes (159 videos with preset slow). You should see three green ticks: **compress**, **deploy / deploy**, **deploy / check**. The **Summary** shows the sizes and "checked 159 video URLs, missing 0".
6. **Report back:** tell Opus and CC that it is done. I will then check the run result and switch `media_base` in tcf-chamber.

**If it goes red:**

- **"over 900 MB":** nothing was committed. Report the number.
- **"Commit videos to main" fails:** redo step 3, then run the workflow again. Videos already done are not skipped, because nothing was committed yet.
- **"check" shows MISSING:** the Pages deploy may still be warming up. Go to Actions → **Deploy Pages** → **Run workflow** once more.

## How tested

- **Workflow files:** both parse as valid YAML.
- **Compress script:** its shell step was run locally, word for word, on 2 files. One of them has an apostrophe in its name (`ch045-tuzi's-dream-chamber.mp4`); URL encoding and output names were both correct. The Summary table and the size lines were written, and ch001 came out the same as in the approved test (3.76 MB → 1.19 MB).
- **`check_urls.py`:** tested against a local server with 2 files present and 1 missing. It reported `MISSING ch002…` and exited with status 1, as intended.
- **`video_list.py`:** lists 159 file names from tcf-chamber's `chambers.json`.
- **Not tested:** the real Actions run and the live site. The sandbox cannot reach GitHub Pages or run Actions.

## Local compression of all 159 (sandbox cross-check)

I also compressed all 159 videos in the sandbox with the same command, to know the total size before the workflow runs. These local files are **not** committed; the workflow makes the real ones.

| | Result |
|---|---|
| Files | 159 / 159 encoded, 0 failures |
| Before | 1,328.8 MB |
| After | **243.6 MB (18%)** |
| Largest compressed file | 5.2 MB (`ch088-thootb-breakthrough-gpt-chamber.mp4`) |
| Time | 18.5 minutes on 4 CPUs. A 2-core GitHub runner will take longer, roughly 40–60 minutes. |

## Not done yet

- **tcf-chamber `media_base`:** the switch to `https://chinsookling.github.io/tcf-chamber-media/videos/` waits until this site is live and the check job shows 0 missing.
- **Phase 4b:** removing `assets/videos/` from the main repo is a later step, after the switch. Tuzi should back up the originals first.

## Risks

- **Downloads from the main site:** the workflow downloads about 1.33 GB from the main site. GitHub-hosted runners handle this easily.
- **The workflow commits straight to `main`,** by design and only when Tuzi runs it. This is the only way to publish the output without an extra PR of about 300 MB.
- **Run time:** preset slow on a 2-core runner can take a while. The job limit is set to 300 minutes.

## Questions for Tuzi

- None.

## Next suggested step

Run the workflow → CC switches `media_base` in tcf-chamber → Phase 4d (nav.js menus) and Phase 4b (redirects and removals).
