# kairos-folder-audit

**English** · [한국어](./README.ko.md)

> A Sunday-morning folder hygiene gate. Made for makers running 30+ side projects.

![demo](./docs/demo.gif)

---

## The 35-repo problem

One Sunday morning, I opened my GitHub and realized I'd been running **35 repositories**. Side projects, K-Series micro SaaS, audit tools, content reels — all alive, all in different states.

Then a thought I'd never had before: _"When did I last open repo #28?"_

I had no idea.

I'd never **measured** my folders. I'd cleaned them, sure — but never measured them. So I asked AI to do it for me.

10 rules. One command. The first run found **40 things** I had no idea were there:
- 4 empty folders forgotten in old projects
- 9 directories without a README, so I couldn't tell what they were
- 9 duplicate files of the same notes scattered across 3 places
- 16 untracked files quietly piling up
- 2 misplaced markdown notes lost at the wrong directory

In 5 minutes I cleaned 18 of them. The rest got logged as **advisory** — visible, archived, not urgent.

But the real win wasn't the cleanup.

**It was setting up a Sunday 06:00 cron** that runs this audit every week. From that point on, I could never _not know_ again.

Automate the inspection — and tidying follows naturally.

That's this tool.

---

## How it actually works (the short version)

```
1. Install once          →  pipx install kairos-folder-audit
2. Run anywhere          →  folder-audit
3. Get an HTML report    →  10 rules, every folder, color-coded
4. (Optional) Sunday cron → auto-runs every week, drops report on Desktop
```

If you can't run code yourself, the gist is still useful: **the 10 things this audit checks are the 10 things any folder system can get wrong**. Treat the list below as a checklist you could apply by hand to your own files. (See "[The 10 things this catches](#the-10-things-this-catches)" below.)

---

## What this is not

To keep expectations sharp:

- ❌ **Not a code linter** — use [Ruff](https://github.com/astral-sh/ruff) for that
- ❌ **Not a secret scanner** — use [Gitleaks](https://github.com/gitleaks/gitleaks) for that
- ❌ **Not an OSPO compliance tool** — use [repolinter](https://github.com/todogroup/repolinter) (RIP, archived 2026-02)
- ❌ **Not a file mover** — use [organize](https://github.com/tfeldmann/organize) for that
- ✅ **Yes:** a weekly hygiene gate for solo makers running too many side projects.

---

## Install

```bash
# Recommended — pipx (isolated, auto-updates)
pipx install kairos-folder-audit

# Or, the fast modern way
uvx kairos-folder-audit

# Or, zero-setup single-file (no package install)
curl -sSL https://raw.githubusercontent.com/sunyoung-lee/kairos-folder-audit/main/folder_audit.py \
  -o folder_audit.py && python3 folder_audit.py
```

Requires Python 3.10+. PyYAML optional, only if you want a custom `rules.yml`.

## Quick start

```bash
# Audit the folder you're standing in
folder-audit

# Audit somewhere else
folder-audit --path ~/projects

# Just the most critical rules (fast)
folder-audit --quick

# CLI output only, skip the HTML
folder-audit --no-html
```

The HTML report drops at `./folder-audit-report.html`. Open it in any browser — there's a dark/light toggle in the corner.

Exit codes are useful in CI: `0` clean · `1` critical found (P0) · `2` action items found (P1).

---

## The 10 things this catches

Even if you never install the tool, this list is the value. These are the 10 ways folder systems quietly degrade:

| ID  | Sev | What it catches                                    | The story                                                 |
| --- | --- | -------------------------------------------------- | --------------------------------------------------------- |
| R01 | P1  | **Empty folders** — 0 files, 0 subdirs             | "I made this folder in 2023 and never used it."           |
| R02 | P2  | **Dormant folders** — README-only, 14+ days idle   | "A project I started, wrote a README, then abandoned."    |
| R03 | P2  | **Missing READMEs**                                | "What is this folder for? I genuinely don't remember."    |
| R04 | P1  | **Duplicate files** — MD5 hash collision           | "Why is `notes.md` in 3 places with identical content?"   |
| R05 | P1  | **Misplaced root `.md`** — YYYYMMDD-* pattern      | "Daily notes scattered at the project root."              |
| R06 | P2  | **Slug convention** — `experiments/<slug>-<NN>`    | "Experiment folders with random names you can't sort."    |
| R07 | P2  | **Large files** — 5MB+ outside `output/` `input/`  | "A 300MB asset I didn't realize was in git."              |
| R08 | P1  | **Unapproved root files**                          | "Random `.zip` files at repo root."                       |
| R09 | P3  | **Untracked git accumulation** — 10+ files         | "git status is unreadable now."                           |
| R10 | P0  | **`.env` protection** — gitignore coverage         | "Wait, did I commit my API keys 6 months ago?"            |

Severity legend: **P0** critical · **P1** action · **P2** advisory · **P3** info.

---

## Configuration

Every rule is externalized in `rules.yml`. Copy it next to the script, edit, and pass `--rules rules.yml`:

```yaml
rules:
  - id: R02
    severity: P2
    title: "Dormant folders"
    enabled: true
    days_threshold: 21        # was 14 — give yourself more slack

  - id: R07
    severity: P2
    title: "Large files"
    enabled: false            # disable for this repo
    size_bytes: 5000000

exclude_dirs:
  - .git
  - node_modules
  - my-custom-skip

approved_root_files:
  - README.md
  - CHANGELOG.md
  - my-tool.config.json       # add anything your project needs at root
```

Run with the custom config:

```bash
folder-audit --rules ./rules.yml --path ~/projects
```

---

## The Sunday 06:00 cron (how I actually use this)

The audit you run once is interesting. The audit that runs **every Sunday at 6 AM without you doing anything** is what changes your habits.

**macOS (launchd):** drop into `~/Library/LaunchAgents/com.user.folder-audit.plist`:

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

Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.user.folder-audit.plist
```

**Linux (crontab):**

```cron
0 6 * * 0  /usr/local/bin/folder-audit --path ~/projects --out ~/folder-audit.html
```

Now when you sit down on Sunday morning, the report is already on your desktop. You don't have to remember to check. You can't unsee what you've measured.

---

## Roadmap

Driven by external review (full research in [research/20260519-deep-folder-audit-launch.md](https://github.com/sunyoung-lee/kairosai/blob/main/research/20260519-deep-folder-audit-launch.md)):

- **v0.2**
  - **R11** Secret content scan (P0) — beyond `.env`, catch AWS keys / private keys / Slack webhooks in `.md`·`.py`·`.json` bodies (Gitleaks-style regex)
  - **R12** Broken symlinks (P2) — `find -xtype l` equivalent
  - **R13** Case-sensitivity collisions (P1) — macOS↔Linux deploy safety
  - Severity rebalancing per CVSS/SonarQube industry standards
- **v0.3**
  - `pre-commit` hook integration
  - TODO/FIXME ownership lint
  - JSON output for CI pipelines

---

## Contributing

It's a single ~400-line file. Easy to fork, easy to adapt.

```bash
git clone https://github.com/sunyoung-lee/kairos-folder-audit
cd kairos-folder-audit
python3 folder_audit.py --path .
```

Issues and PRs welcome.

## License

[MIT](./LICENSE) © 2026 Sunny Lee

---

## Background

Part of the [kairos](https://instagram.com/sun.young.0207) toolset — a personal harness for running 35+ side projects as a solo indie maker.

If you're curious about the broader system, watch the build, or just want to see what running this many things solo actually looks like:

- 📷 Instagram — [@sun.young.0207](https://instagram.com/sun.young.0207)
- 🧵 Threads — [@sun.young.0207](https://threads.net/@sun.young.0207)

The launch reel for this tool went up there first.
