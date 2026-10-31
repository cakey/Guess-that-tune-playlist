# Guess That Tune playlist backups

This repository is public on GitHub (`cakey/Guess-that-tune-playlist`). Keep
it to the playlist backups and the code that produces them; see `README`.

## What belongs here

- The backup files (`*-backup-readable.txt`, `*-backup-track-urls.txt`).
- `backup.py`, `scripts/`, the `launchd/` template, `README` and this file.

## What doesn't

Listening analysis, Last.fm data, taste notes, recommendations, and notes on
how Ben uses each playlist. Those live in Ben's private, local-only
`~/Projects/skills` repository: taste notes in `TASTE.md`, Last.fm data and
generated analyses under `concert-radar/data/private/`. Put scratch analysis
in a temp directory, never in this folder, even uncommitted.

## Keeping it clean

`.gitignore` is an allowlist: it ignores everything except the files above, so
nothing else can be committed by accident. Only add an entry for a new file
after checking it belongs in public. The monthly job
(`scripts/run-backup.zsh`) commits only backup files and pushes `master`.
