# kairos-folder-audit

**English** · [한국어](./README.ko.md)

> **One command. 10 checks. Weekly auto-run. Folder peace of mind.**

![demo](./docs/demo.gif)

## Install

```bash
pipx install git+https://github.com/sunyoung-lee/kairos-folder-audit.git
```

No pipx? Ask your AI agent to install it for your OS.

## Use

```bash
folder-audit
```

Generates an HTML report and auto-opens it. Korean speakers get Korean output automatically.

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
- **P1 action** — Address within the week. Structural integrity.
- **P2 advisory** — Address within the month. Maintainability.
- **P3 info** — Awareness only. No urgent action.
- **Clean** — Nothing found. Healthy.

## What to do after a run

Ask your AI agent:

> _"Open this folder-audit report and fix the P0 and P1 findings. Show me each change before applying."_

The agent reads the report, plans the fixes, and applies them after your approval.

## Auto every Sunday

Ask your AI agent:

> _"Set up a weekly job that runs `folder-audit` on my projects every Sunday 6 AM, saves the report to my Desktop, with `--no-open`."_

The agent handles your OS, paths, and scheduler. Review before applying.

Set it once. Stop remembering.

## License

[MIT](./LICENSE) © 2026 Sunny Lee

—

[@sun.young.0207](https://instagram.com/sun.young.0207) — Instagram · [Threads](https://threads.net/@sun.young.0207)
