# kairos-folder-audit

**English** · [한국어](./README.ko.md)

> **10 rules. Sunday 06:00. HTML report. For makers running 30+ side projects.**

A folder hygiene health-check CLI that runs 10 configurable rules across your filesystem and emits a sortable HTML report (dark/light toggle, zero dependencies for the core checks).

Built by [@sun.young.0207](https://instagram.com/sun.young.0207) for the 35-repo problem — "I have 35 GitHub repos. When did I last open repo #28?"

![Folder Audit Report screenshot — dark mode](docs/screenshot-dark.png)

## What it is

A **single-file Python script** that walks your folder tree, applies 10 rules (empty dirs, dormant folders, README gaps, MD5 duplicates, misplaced root files, slug convention, large files, root whitelist, untracked git accumulation, .env protection), and renders a self-contained HTML report you can share, archive, or wire into a Sunday cron.

## What it is NOT

- ❌ A code linter (use [Ruff](https://github.com/astral-sh/ruff))
- ❌ A secret scanner (use [Gitleaks](https://github.com/gitleaks/gitleaks))
- ❌ An OSPO compliance tool (use [repolinter](https://github.com/todogroup/repolinter) — RIP, archived 2026-02)
- ❌ A file mover or auto-organizer (use [organize](https://github.com/tfeldmann/organize))
- ✅ **A Sunday-morning folder hygiene gate for indie makers running 30+ repos.**

## Install

```bash
# Recommended — pipx (isolated, auto-updates)
pipx install kairos-folder-audit

# Alternative — uv (faster, modern)
uvx kairos-folder-audit

# Zero-setup — single-file curl (no package install)
curl -sSL https://raw.githubusercontent.com/sunyoung-lee/kairos-folder-audit/main/folder_audit.py \
  -o folder_audit.py && python3 folder_audit.py
```

Requires Python 3.10+. PyYAML optional (only if you customize `rules.yml`).

## Quick start

```bash
# Audit current directory
folder-audit

# Audit specific path
folder-audit --path ~/projects

# Quick mode (R01/R02/R04 only)
folder-audit --quick

# CLI output only, no HTML
folder-audit --no-html

# Filter by severity
folder-audit --severity p0
```

The HTML report lands at `./folder-audit-report.html` by default. Override with `--out path/to/report.html`.

## The 10 rules

| ID  | Severity | Title                                              | What it catches                                                 |
| --- | -------- | -------------------------------------------------- | --------------------------------------------------------------- |
| R01 | P1       | Empty folders                                      | Directories with 0 files and 0 subdirs                          |
| R02 | P2       | Dormant folders (README-only, 14+ days idle)       | Forgotten projects: a single README, no other activity          |
| R03 | P2       | Missing README in top-level folder                 | Top-level dirs without `README.md` (configurable whitelist)     |
| R04 | P1       | Duplicate files (MD5 hash collision)               | Text files with identical content across the tree               |
| R05 | P1       | Misplaced root *.md (YYYYMMDD-* pattern)           | Date-prefixed notes scattered at repo root instead of `reports/`|
| R06 | P2       | Experiments slug convention                        | `experiments/<slug>-<NN>` enforcement (configurable)            |
| R07 | P2       | Large files (5MB+, outside `output/` `input/`)     | Binaries that should be in storage or gitignored                |
| R08 | P1       | Unapproved root files                              | Anything at repo root not in `approved_root_files`              |
| R09 | P3       | Untracked git files accumulation (10+)             | git status pollution risk                                       |
| R10 | P0       | `.env` protection gate                             | `.env` files not covered by `.gitignore`                        |

Severity legend: **P0** critical · **P1** action · **P2** advisory · **P3** info.
Exit codes: `0` clean · `1` P0 found · `2` P1 found (P2/P3 don't fail).

## Configuration

All rules are externalized in `rules.yml` — copy it next to the script and pass `--rules rules.yml`:

```yaml
rules:
  - id: R02
    severity: P2
    title: "Dormant folders"
    enabled: true
    days_threshold: 21       # was 14

  - id: R07
    severity: P2
    title: "Large files"
    enabled: false           # disable for this repo
    size_bytes: 5000000

exclude_dirs:
  - .git
  - node_modules
  - my-custom-skip

approved_root_files:
  - README.md
  - CHANGELOG.md
  - my-tool.config.json     # add your project's root files
```

Run with custom config:

```bash
folder-audit --rules ./rules.yml --path ~/projects
```

## Sunday 06:00 cron (macOS launchd)

The way I actually use this. Drop into `~/Library/LaunchAgents/com.user.folder-audit.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.user.folder-audit</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/folder-audit</string>
    <string>--path</string><string>/Users/YOU/projects</string>
    <string>--out</string><string>/Users/YOU/Desktop/folder-audit.html</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key><integer>0</integer>
    <key>Hour</key><integer>6</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
</dict>
</plist>
```

Then `launchctl load ~/Library/LaunchAgents/com.user.folder-audit.plist`.

For Linux, use crontab:

```cron
0 6 * * 0  /usr/local/bin/folder-audit --path ~/projects --out ~/folder-audit.html
```

## Why this exists

If you've ever:
- Forgotten which side-project repo you were last working on
- Found 4 copies of the same `notes.md` across 3 folders
- Discovered a `.env` file you'd committed 6 months ago
- Had a 300MB asset you forgot was in `git`

…this is the Sunday-morning gate that catches all four before they grow.

## Roadmap (v0.2+)

Driven by external validation research, planned for future versions:

- **R11** Secret content scan (P0) — beyond `.env`, catch AWS keys / private keys / Slack webhooks in `.md`·`.py`·`.json` bodies (Gitleaks-style regex)
- **R12** Broken symlinks (P2) — `find -xtype l` equivalent
- **R13** Case-sensitivity collisions (P1) — macOS↔Linux deploy safety
- Severity rebalancing per CVSS/SonarQube industry standards (R01→P3, R04→P2, R05→P2)
- TODO/FIXME ownership lint
- `pre-commit` hook integration

## Contributing

Issues and PRs welcome. This is a single-file script (~400 lines) — easy to fork, easy to adapt.

```bash
git clone https://github.com/sunyoung-lee/kairos-folder-audit
cd kairos-folder-audit
python3 folder_audit.py --path .   # dogfood
```

## License

[MIT](./LICENSE) © 2026 Sunny Lee

## Background

Part of the [kairos](https://instagram.com/sun.young.0207) toolset — a personal harness for running 35+ side projects as a solo indie maker. If you're curious about the broader system or want to follow the build, the project reel is on [Instagram](https://instagram.com/sun.young.0207).
