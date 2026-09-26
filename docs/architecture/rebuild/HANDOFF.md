# HANDOFF — Phase 4g (tcf-chamber-media: license wording)

- **Phase:** 4g — the same license rule as tcf-chamber (Phase 4f)
- **Branch:** `phase-4g-license` from `main` @ `728d754`
- **Related:** `the-Civilisation-field` has its own `phase-4g-license` PR.
- **Current owner:** Claude Code → next: Opus review → Tuzi merges
- Previous handoff (video phase): `git show a565e2e:docs/architecture/rebuild/HANDOFF.md`

## What changed

| File | Before | After |
|---|---|---|
| `README.md` (License) | "Original content is licensed under CC BY 4.0 (…). AI and guest responses are preserved as records; their rights depend on each case." | "All content — chamber images, invitation texts (by Tuzi or by an AI affiliate), and videos, including every video in this repo — is licensed under CC BY 4.0 (…). Please credit: Tuzi and Affiliates, The Civilisation Field, with a link to https://chinsookling.github.io/tcf-chamber/. Responses from guests are kept as records; their rights depend on each case." |
| `index.html` | "Original content is licensed under CC BY 4.0. Reading is not permission to act." | The same rule ("…including these videos…"), with links to CC BY 4.0 and to The Chamber, then "Reading is not permission to act." |

- **Wording:** this matches tcf-chamber's `license/`, with "videos" made explicit, because this repo holds the videos.
- **Credit link:** it points to The Chamber, where the videos are shown. This repo has no license page of its own.
- **Not changed:** workflows, tools and `videos/`.

## Grep (excluding `.git` and `docs/architecture/`)

- "Original content", "AI and guest responses": **0**.
- "depend on each case": `README.md` and `index.html`, **guest responses only**.

## How tested

- **Grep:** the results above.
- **Diff:** 2 files, text only.
