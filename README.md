# kairos-folder-audit

**English** · [한국어](./README.ko.md)

> **One command. 10 checks. Weekly auto-run. Folder peace of mind.**

![demo](./docs/demo.gif)

## Install

```bash
# Recommended
pipx install git+https://github.com/sunyoung-lee/kairos-folder-audit.git

# Or uvx (no install)
uvx --from git+https://github.com/sunyoung-lee/kairos-folder-audit.git folder-audit

# Or single-file (zero setup)
curl -sSL https://raw.githubusercontent.com/sunyoung-lee/kairos-folder-audit/main/folder_audit.py -o folder_audit.py && python3 folder_audit.py
```

## Use

```bash
folder-audit
```

Generates `./folder-audit-report.html` and **auto-opens it in your browser**. Detects language from `$LANG` (Korean speakers get Korean output automatically).

Skip auto-open: `--no-open`. Force language: `--lang en` or `--lang ko`.

## What you get

- **One command**, full folder audit
- **HTML report** — save, share, open later
- **Weekly auto-run** — set once, never check manually
- **No more stress** — "did I commit `.env` 6 months ago?" never again

## Who this is for

- Solo indie makers running **5+ side projects** at once
- AI pair coders shipping with **Claude Code / Cursor** daily
- Anyone with **200+ files** across repos, Notion, or Drive
- People who keep thinking _"what was this folder for again?"_

## When to use it

- **Sunday morning** — light check before the new week
- **Before a new project** — tidy what you already have
- **After 6 months of chaos** — bulk cleanup, see everything at once
- **Before pushing public** — catch `.env` leaks, duplicates, large files
- **Right after an AI pair session** — clean up leftover artifacts

## Sample report

![report](./docs/report-dark.png)

## The 10 checks

| ID  | Sev | Catches                                          |
| --- | --- | ------------------------------------------------ |
| R01 | P1  | Empty folders                                    |
| R02 | P2  | Dormant folders (README-only, 14+ days idle)     |
| R03 | P2  | Missing README                                   |
| R04 | P1  | Duplicate files (MD5)                            |
| R05 | P1  | Misplaced root `.md` (YYYYMMDD-* pattern)        |
| R06 | P2  | Experiments slug convention                      |
| R07 | P2  | Large files (5MB+)                               |
| R08 | P1  | Unapproved root files                            |
| R09 | P3  | Untracked git accumulation (10+)                 |
| R10 | P0  | `.env` protection                                |

## Severity legend

- **P0 critical** — Fix immediately. Security or data-loss risk.
- **P1 action** — Address within the week. Structural integrity or build impact.
- **P2 advisory** — Address within the month. Maintainability and clarity.
- **P3 info** — Awareness only. No urgent action needed.
- **Clean** — Rule found nothing in this area. Healthy.

## What to do after a run

Open the report, and for each finding choose one of:

1. **Fix now** (recommended for P0 / P1) — apply the suggested action shown in the report
2. **Archive as advisory** (P2 / P3) — leave for next week's batch cleanup
3. **Whitelist** — if it's a false positive (e.g., a folder you intentionally keep empty), add it to `rules.yml`

Quick fixes by rule:

- **R01 empty folder** → `rmdir <path>/` or add `.gitkeep` if intentional
- **R03 missing README** → add a 1-line `README.md`, or add the folder to `standard_child` in `rules.yml`
- **R04 duplicate** → keep one canonical, `git rm` the others or stub them with a `moved_to:` pointer
- **R05 misplaced `.md`** → `git mv <file> reports/<file>` or `research/<file>`
- **R10 `.env` exposed** → `echo ".env" >> .gitignore && git rm --cached .env` immediately

After the first cleanup, set up the [Sunday cron](#auto-every-sunday) below. That's the real win — audit becomes background, not a chore.

## Auto every Sunday

```cron
0 6 * * 0  folder-audit --path ~/projects --out ~/folder-audit.html
```

Set this once. Report lands on your desktop every Sunday 6 AM. Stop remembering.

## License

[MIT](./LICENSE) © 2026 Sunny Lee

—

[@sun.young.0207](https://instagram.com/sun.young.0207) — Instagram · [Threads](https://threads.net/@sun.young.0207)
