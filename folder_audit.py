#!/usr/bin/env python3
"""
folder_audit.py — folder hygiene health-check with 10 configurable rules.

Walks a folder tree, runs 10 rules (empty dirs / dormant dirs / README missing /
MD5 duplicates / misplaced root *.md / slug convention / large files / approved
root whitelist / untracked git accumulation / .env protection), and emits a
sortable HTML report.

Usage:
    python3 folder_audit.py                     # audit current directory
    python3 folder_audit.py --path ~/projects   # audit specific path
    python3 folder_audit.py --rules my.yml      # custom rules config
    python3 folder_audit.py --quick             # only R1/R2/R4 (fast)
    python3 folder_audit.py --severity p0       # filter by severity
    python3 folder_audit.py --no-html           # CLI output only

Repo: https://github.com/sunyoung-lee/kairos-folder-audit
License: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from html import escape
from pathlib import Path

# Optional yaml support — falls back to embedded defaults if PyYAML missing
try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

NOW_LABEL = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TODAY = datetime.now().strftime("%Y%m%d")

# ─── i18n ──────────────────────────────────────────────────────────────
LOCALES = {
    "en": {
        "report_title": "Folder Audit Report",
        "report_sub":   "{now} · root: {root}",
        "stat_p0":      "P0 critical",
        "stat_p1":      "P1 action",
        "stat_p2":      "P2 advisory",
        "stat_p3":      "P3 info",
        "stat_clean":   "Clean rules",
        "stat_total":   "Total findings",
        "lab_finding":  "finding",
        "lab_findings": "findings",
        "lab_clean":    "✓ clean",
        "lab_passed":   "0 findings — passed",
        "footer":       "kairos-folder-audit · MIT License",
        "cli_header":   "🔎  folder audit · {now}",
        "cli_total":    "Total: {n} findings",
        "cli_html":     "✓ HTML: {path}",
        "cli_open":     "  open {path}",
        "cli_more":     "      … and {n} more",
    },
    "ko": {
        "report_title": "폴더 감사 리포트",
        "report_sub":   "{now} · 경로: {root}",
        "stat_p0":      "P0 차단",
        "stat_p1":      "P1 액션",
        "stat_p2":      "P2 권고",
        "stat_p3":      "P3 안내",
        "stat_clean":   "Clean 룰",
        "stat_total":   "총 finding",
        "lab_finding":  "건",
        "lab_findings": "건",
        "lab_clean":    "✓ 통과",
        "lab_passed":   "0건 — 통과",
        "footer":       "kairos-folder-audit · MIT License",
        "cli_header":   "🔎  폴더 감사 · {now}",
        "cli_total":    "총: {n}건",
        "cli_html":     "✓ HTML 생성: {path}",
        "cli_open":     "  open {path}",
        "cli_more":     "      … 외 {n}건",
    },
}

RULE_TITLES = {
    "en": {
        "R01": "Empty folders (0 files, 0 subdirs)",
        "R02": "Dormant folders (README-only, 14+ days idle)",
        "R03": "Missing README in top-level folder",
        "R04": "Duplicate files (MD5 hash collision)",
        "R05": "Misplaced root *.md (YYYYMMDD-* pattern)",
        "R06": "Experiments slug convention violation",
        "R07": "Large files (5MB+, outside output/input)",
        "R08": "Unapproved root files",
        "R09": "Untracked git files accumulation (10+)",
        "R10": ".env protection gate (.gitignore coverage)",
    },
    "ko": {
        "R01": "빈 폴더 (파일 0개, 하위 0개)",
        "R02": "Dormant 폴더 (README만, 14일+ 변경 없음)",
        "R03": "상위 폴더 README 누락",
        "R04": "중복 파일 (MD5 해시 충돌)",
        "R05": "Misplaced 루트 *.md (YYYYMMDD-* 패턴)",
        "R06": "Experiments 슬러그 컨벤션 위반",
        "R07": "거대 파일 (5MB+, output/input 제외)",
        "R08": "화이트리스트 외 루트 파일",
        "R09": "Untracked git 누적 (10건+)",
        "R10": ".env 보호 게이트 (.gitignore 커버리지)",
    },
}


def detect_lang() -> str:
    """Auto-detect language from $LANG / $LC_ALL. Defaults to en."""
    raw = (os.environ.get("LANG", "") or os.environ.get("LC_ALL", "")).lower()
    if raw.startswith("ko"):
        return "ko"
    return "en"


def open_in_browser(path: Path) -> None:
    """Open HTML in default browser. Silent on failure."""
    try:
        system = platform.system()
        if system == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        elif system == "Linux":
            subprocess.run(["xdg-open", str(path)], check=False, stderr=subprocess.DEVNULL)
        elif system == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]
    except Exception:
        pass

# ─── Default config (used when rules.yml absent) ──────────────────────
DEFAULT_CONFIG = {
    "exclude_dirs": [
        ".git", "node_modules", ".next", "dist", "build", "__pycache__",
        ".venv", "venv", ".pytest_cache", ".mypy_cache", ".turbo",
        ".cache", "coverage", ".vercel", ".netlify",
    ],
    "standard_child": [
        "input", "output", "scripts", "prompts", "copy",
        "templates", "guides", "rules", "adr", "src", "tests",
    ],
    "approved_root_files": [
        "README.md", "CHANGELOG.md", "LICENSE", "Makefile",
        "package.json", ".gitignore", ".npmrc", ".env.example",
    ],
    "rules": [
        {"id": "R01", "severity": "P1", "title": "Empty folders (0 files, 0 subdirs)",          "enabled": True},
        {"id": "R02", "severity": "P2", "title": "Dormant folders (README-only, 14+ days idle)", "enabled": True, "days_threshold": 14},
        {"id": "R03", "severity": "P2", "title": "Missing README in top-level folder",           "enabled": True},
        {"id": "R04", "severity": "P1", "title": "Duplicate files (MD5 hash collision)",         "enabled": True},
        {"id": "R05", "severity": "P1", "title": "Misplaced root *.md (YYYYMMDD-* pattern)",     "enabled": True},
        {"id": "R06", "severity": "P2", "title": "Experiments slug convention violation",        "enabled": True, "folder": "experiments"},
        {"id": "R07", "severity": "P2", "title": "Large files (5MB+, outside output/input)",     "enabled": True, "size_bytes": 5_000_000},
        {"id": "R08", "severity": "P1", "title": "Unapproved root files",                        "enabled": True},
        {"id": "R09", "severity": "P3", "title": "Untracked git files accumulation (10+)",       "enabled": True, "min_count": 10},
        {"id": "R10", "severity": "P0", "title": ".env protection gate (.gitignore coverage)",   "enabled": True},
    ],
}

# ─── Config loader ─────────────────────────────────────────────────────
def load_config(rules_path: Path | None, lang: str = "en") -> dict:
    if rules_path and rules_path.exists():
        if not HAS_YAML:
            print("⚠  PyYAML not installed; using built-in defaults. `pip install pyyaml` for custom rules.", file=sys.stderr)
            cfg = dict(DEFAULT_CONFIG)
        else:
            with open(rules_path) as f:
                cfg = yaml.safe_load(f) or DEFAULT_CONFIG
    else:
        cfg = {k: (list(v) if isinstance(v, list) else v) for k, v in DEFAULT_CONFIG.items()}
        cfg["rules"] = [dict(r) for r in DEFAULT_CONFIG["rules"]]

    # Apply localized rule titles (only when using built-in defaults; user-provided
    # rules.yml titles are kept as-is — user is responsible for their own i18n)
    if not (rules_path and rules_path.exists()) and lang in RULE_TITLES:
        titles = RULE_TITLES[lang]
        for rule in cfg["rules"]:
            if rule["id"] in titles:
                rule["title"] = titles[rule["id"]]
    return cfg

# ─── Rule implementations ──────────────────────────────────────────────
def walk_dirs(root: Path, exclude_dirs: set[str]):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs and not d.startswith(".")]
        yield Path(dirpath), dirnames, filenames


def r01_empty_folders(root: Path, cfg: dict, _rule: dict):
    findings = []
    for dirpath, dirnames, filenames in walk_dirs(root, set(cfg["exclude_dirs"])):
        rel = dirpath.relative_to(root)
        if str(rel) == ".":
            continue
        if not filenames and not dirnames:
            findings.append({
                "path": str(rel),
                "msg": "0 files, 0 subdirs",
                "action": f"rmdir {rel}/  OR  add .gitkeep if intentional",
            })
    return findings


def r02_dormant_folders(root: Path, cfg: dict, rule: dict):
    findings = []
    days = rule.get("days_threshold", 14)
    threshold = datetime.now() - timedelta(days=days)
    for dirpath, dirnames, filenames in walk_dirs(root, set(cfg["exclude_dirs"])):
        rel = dirpath.relative_to(root)
        if str(rel) == "." or len(rel.parts) > 1:
            continue
        if len(filenames) <= 1 and dirnames == [] and any(f.lower().startswith("readme") for f in filenames):
            mtimes = [datetime.fromtimestamp((dirpath / f).stat().st_mtime) for f in filenames]
            if mtimes and max(mtimes) < threshold:
                findings.append({
                    "path": str(rel),
                    "msg": f"README only, last change {max(mtimes).strftime('%Y-%m-%d')}",
                    "action": "decide: migrate / archive / re-activate",
                })
    return findings


def r03_missing_readme(root: Path, cfg: dict, _rule: dict):
    findings = []
    exclude = set(cfg["exclude_dirs"])
    standard = set(cfg["standard_child"])
    for entry in sorted(root.iterdir()):
        if not entry.is_dir() or entry.name in exclude or entry.name.startswith("."):
            continue
        if entry.name in standard:
            continue
        files = list(entry.iterdir())
        if not files:
            continue  # caught by R01
        if not any(f.name.lower().startswith("readme") for f in files if f.is_file()):
            findings.append({
                "path": entry.name + "/",
                "msg": "no README.md",
                "action": "add a one-line README, or add folder name to standard_child in rules.yml",
            })
    return findings


def r04_md5_duplicates(root: Path, cfg: dict, _rule: dict):
    findings = []
    exclude = set(cfg["exclude_dirs"])
    by_hash = defaultdict(list)
    text_ext = {".md", ".txt", ".html", ".json", ".yaml", ".yml", ".sh", ".py", ".mjs", ".ts", ".js"}
    for dirpath, _dirnames, filenames in walk_dirs(root, exclude):
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix not in text_ext:
                continue
            try:
                if p.stat().st_size > 5_000_000:
                    continue
                h = hashlib.md5(p.read_bytes()).hexdigest()
                by_hash[h].append(str(p.relative_to(root)))
            except Exception:
                pass
    for h, paths in by_hash.items():
        if len(paths) > 1:
            findings.append({
                "path": " ≡ ".join(paths),
                "msg": f"MD5 {h[:8]} · {len(paths)} files",
                "action": "keep 1 canonical, stub others (moved_to:) or git rm",
            })
    return findings


def r05_misplaced_root_md(root: Path, cfg: dict, _rule: dict):
    findings = []
    approved = set(cfg["approved_root_files"])
    for entry in root.glob("*.md"):
        name = entry.name
        if name in approved:
            continue
        if re.match(r"^\d{8}-", name):
            findings.append({
                "path": name,
                "msg": "YYYYMMDD-* root file (likely belongs in reports/ or research/)",
                "action": f"git mv {name} reports/{name}",
            })
        else:
            findings.append({
                "path": name,
                "msg": "non-standard root .md",
                "action": "add to approved_root_files in rules.yml, or migrate, or delete",
            })
    return findings


def r06_experiments_slug(root: Path, _cfg: dict, rule: dict):
    findings = []
    folder = rule.get("folder", "experiments")
    exp = root / folder
    if not exp.exists():
        return findings
    pattern = re.compile(r"^[a-z][a-z0-9-]*-(\d{2}|[a-z][a-z0-9]*)$")
    for entry in sorted(exp.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if not pattern.match(entry.name):
            findings.append({
                "path": f"{folder}/{entry.name}/",
                "msg": "slug-NN pattern violation (expected: my-slug-01, my-slug-02, ...)",
                "action": f"git mv {folder}/{entry.name} {folder}/{entry.name}-01",
            })
    return findings


def r07_large_files(root: Path, cfg: dict, rule: dict):
    findings = []
    threshold = rule.get("size_bytes", 5_000_000)
    skip_dirs = {"output", "input"}
    for dirpath, _dirnames, filenames in walk_dirs(root, set(cfg["exclude_dirs"])):
        rel = Path(dirpath).relative_to(root)
        if any(p in skip_dirs for p in rel.parts):
            continue
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                size = p.stat().st_size
            except Exception:
                continue
            if size >= threshold:
                findings.append({
                    "path": str(p.relative_to(root)),
                    "msg": f"{size / 1024 / 1024:.1f} MB",
                    "action": "move to input/, output/, .gitignore, or external storage (S3/R2/Drive)",
                })
    return findings


def r08_unapproved_root(root: Path, cfg: dict, _rule: dict):
    findings = []
    approved = set(cfg["approved_root_files"])
    for entry in sorted(root.iterdir()):
        if not entry.is_file():
            continue
        if entry.name in approved or entry.name.startswith("."):
            continue
        if entry.suffix == ".md":
            continue  # handled by R05
        findings.append({
            "path": entry.name,
            "msg": f"{entry.stat().st_size} bytes · not in approved_root_files",
            "action": "add to approved_root_files in rules.yml, or migrate, or delete",
        })
    return findings


def r09_untracked_accumulation(root: Path, _cfg: dict, rule: dict):
    findings = []
    min_count = rule.get("min_count", 10)
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "status", "--short"],
            capture_output=True, text=True, timeout=10,
        ).stdout
        untracked = [ln for ln in out.splitlines() if ln.startswith("??")]
        if len(untracked) >= min_count:
            findings.append({
                "path": "(repo root)",
                "msg": f"{len(untracked)} untracked entries — git history pollution risk",
                "action": "review with `git status` → commit intentional, gitignore/rm the rest",
            })
            for ln in untracked[:15]:
                findings.append({
                    "path": ln[3:].strip(),
                    "msg": "untracked",
                    "action": "classify: commit / gitignore / rm",
                })
    except FileNotFoundError:
        pass  # not a git repo, skip silently
    except Exception as e:
        findings.append({"path": "(git)", "msg": f"git status failed: {e}", "action": "manual check"})
    return findings


def r10_env_protection(root: Path, cfg: dict, _rule: dict):
    findings = []
    gitignore_path = root / ".gitignore"
    gitignore = gitignore_path.read_text(errors="ignore") if gitignore_path.exists() else ""
    protects_env = bool(re.search(r"^\.env(\.|$|\s)", gitignore, re.MULTILINE)) or "*.env" in gitignore or "**/.env" in gitignore

    for dirpath, _dirnames, filenames in walk_dirs(root, set(cfg["exclude_dirs"])):
        for fn in filenames:
            if fn == ".env":
                p = Path(dirpath) / fn
                rel = p.relative_to(root)
                try:
                    out = subprocess.run(
                        ["git", "-C", str(root), "check-ignore", str(rel)],
                        capture_output=True, text=True, timeout=5,
                    )
                    if out.returncode != 0:
                        findings.append({
                            "path": str(rel),
                            "msg": "git check-ignore miss — commit risk",
                            "action": "add `.env` to .gitignore (global or local)",
                        })
                except FileNotFoundError:
                    pass  # not a git repo
                except Exception:
                    pass
    if not protects_env and not gitignore_path.exists():
        findings.append({
            "path": ".gitignore",
            "msg": "no .gitignore present",
            "action": "create .gitignore with `.env` rule",
        })
    return findings


RULE_FNS = {
    "R01": r01_empty_folders, "R02": r02_dormant_folders, "R03": r03_missing_readme,
    "R04": r04_md5_duplicates, "R05": r05_misplaced_root_md, "R06": r06_experiments_slug,
    "R07": r07_large_files, "R08": r08_unapproved_root, "R09": r09_untracked_accumulation,
    "R10": r10_env_protection,
}


def run_all_rules(root: Path, cfg: dict, quick: bool = False, severity_filter: str | None = None):
    results = {}
    rules = cfg["rules"]
    if quick:
        rules = [r for r in rules if r["id"] in ("R01", "R02", "R04")]
    if severity_filter:
        rules = [r for r in rules if r["severity"].lower() == severity_filter.lower()]
    for rule in rules:
        if not rule.get("enabled", True):
            continue
        rid = rule["id"]
        fn = RULE_FNS.get(rid)
        if fn is None:
            continue
        try:
            findings = fn(root, cfg, rule)
        except Exception as e:
            findings = [{"path": "(error)", "msg": str(e), "action": "manual check"}]
        results[rid] = {"sev": rule["severity"], "title": rule["title"], "findings": findings}
    return results


# ─── HTML output ───────────────────────────────────────────────────────
HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>folder audit · {NOW}</title>
<style>
  :root {{ --bg:#FAFAF9; --ink:#0B1220; --muted:#64748B; --line:#E2E8F0;
           --accent:#0EA5A5; --ok:#16a34a; --warn:#f59e0b; --crit:#dc2626; --info:#0284c7; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#0B1220; --ink:#F8FAFC; --muted:#94A3B8; --line:#1E293B; }}
  }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
          background:var(--bg); color:var(--ink); margin:0; padding:32px 24px;
          line-height:1.6; max-width:1200px; margin:0 auto; }}
  h1 {{ font-size:28px; margin:0 0 6px; letter-spacing:-0.02em; }}
  .sub {{ color:var(--muted); font-size:14px; margin-bottom:24px; }}
  .summary {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr));
              gap:12px; margin-bottom:32px; }}
  .stat {{ background:var(--bg); border:1px solid var(--line); border-radius:10px; padding:14px 16px; }}
  .stat .n {{ font-size:28px; font-weight:800; line-height:1; }}
  .stat .l {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:0.05em; }}
  .stat.p0 .n {{ color:var(--crit); }} .stat.p1 .n {{ color:var(--accent); }}
  .stat.p2 .n {{ color:var(--warn); }} .stat.p3 .n {{ color:var(--info); }}
  .stat.clean .n {{ color:var(--ok); }}
  .rule {{ border:1px solid var(--line); border-radius:12px; margin-bottom:18px; overflow:hidden; }}
  .rule-h {{ padding:14px 18px; background:rgba(0,0,0,0.025); display:flex;
             justify-content:space-between; align-items:center; gap:12px; }}
  @media (prefers-color-scheme: dark) {{ .rule-h {{ background:rgba(255,255,255,0.04); }} }}
  .rule-id {{ font-family:ui-monospace,SFMono-Regular,monospace; font-weight:700;
              padding:3px 8px; border-radius:6px; font-size:12px; background:var(--ink); color:var(--bg); }}
  .sev {{ font-family:ui-monospace,monospace; font-size:11px; font-weight:700;
          padding:2px 7px; border-radius:4px; }}
  .sev.p0 {{ background:var(--crit); color:#fff; }} .sev.p1 {{ background:var(--accent); color:#fff; }}
  .sev.p2 {{ background:var(--warn); color:#fff; }} .sev.p3 {{ background:var(--info); color:#fff; }}
  .count {{ color:var(--muted); font-size:13px; font-family:ui-monospace,monospace; }}
  .f {{ padding:12px 18px; border-top:1px solid var(--line); display:grid; gap:6px; }}
  .f-path {{ font-family:ui-monospace,monospace; font-weight:600; font-size:13px;
             color:var(--accent); word-break:break-all; }}
  .f-msg {{ color:var(--ink); font-size:14px; }}
  .f-action {{ color:var(--muted); font-size:13px; font-family:ui-monospace,monospace;
               background:rgba(0,0,0,0.03); padding:6px 10px; border-radius:6px; }}
  @media (prefers-color-scheme: dark) {{ .f-action {{ background:rgba(255,255,255,0.04); }} }}
  .clean {{ padding:16px 18px; color:var(--ok); font-weight:600; }}
  .footer {{ color:var(--muted); font-size:12px; margin-top:48px; text-align:center;
             border-top:1px solid var(--line); padding-top:24px; }}
  .footer a {{ color:var(--accent); }}
  code {{ font-family:ui-monospace,monospace; background:rgba(0,0,0,0.06);
          padding:1px 5px; border-radius:4px; font-size:13px; }}
  @media (prefers-color-scheme: dark) {{ code {{ background:rgba(255,255,255,0.08); }} }}
  html[data-theme="light"] {{ --bg:#FAFAF9 !important; --ink:#0B1220 !important;
    --muted:#64748B !important; --line:#E2E8F0 !important; }}
  html[data-theme="dark"] {{ --bg:#0B1220 !important; --ink:#F8FAFC !important;
    --muted:#94A3B8 !important; --line:#1E293B !important; }}
  .theme-toggle {{ position:fixed; top:16px; right:16px;
    background:var(--bg); color:var(--ink); border:1px solid var(--line);
    border-radius:999px; padding:6px 12px; font-size:13px; cursor:pointer;
    font-family:inherit; user-select:none; z-index:100; }}
  .theme-toggle:hover {{ border-color:var(--accent); color:var(--accent); }}
</style>
<script>
  (function() {{
    var saved = localStorage.getItem('folder-audit-theme') || 'auto';
    if (saved !== 'auto') document.documentElement.setAttribute('data-theme', saved);
    window.cycleTheme = function() {{
      var cur = localStorage.getItem('folder-audit-theme') || 'auto';
      var next = cur === 'auto' ? 'light' : (cur === 'light' ? 'dark' : 'auto');
      localStorage.setItem('folder-audit-theme', next);
      if (next === 'auto') document.documentElement.removeAttribute('data-theme');
      else document.documentElement.setAttribute('data-theme', next);
      document.querySelector('.theme-toggle').textContent = next === 'auto' ? '🌓 Auto' : (next === 'light' ? '☀ Light' : '🌙 Dark');
    }};
    window.addEventListener('DOMContentLoaded', function() {{
      var t = document.querySelector('.theme-toggle');
      if (t) t.textContent = saved === 'auto' ? '🌓 Auto' : (saved === 'light' ? '☀ Light' : '🌙 Dark');
    }});
  }})();
</script>
</head>
<body>
<button class="theme-toggle" onclick="cycleTheme()">🌓 Auto</button>
<h1>{L_TITLE}</h1>
<div class="sub">{NOW} · root: <code>{ROOT}</code></div>
<div class="summary">
  <div class="stat p0"><div class="n">{P0}</div><div class="l">{L_P0}</div></div>
  <div class="stat p1"><div class="n">{P1}</div><div class="l">{L_P1}</div></div>
  <div class="stat p2"><div class="n">{P2}</div><div class="l">{L_P2}</div></div>
  <div class="stat p3"><div class="n">{P3}</div><div class="l">{L_P3}</div></div>
  <div class="stat clean"><div class="n">{CLEAN}</div><div class="l">{L_CLEAN}</div></div>
  <div class="stat"><div class="n">{TOTAL}</div><div class="l">{L_TOTAL}</div></div>
</div>
{RULES_HTML}
<div class="footer">
  <a href="https://github.com/sunyoung-lee/kairos-folder-audit">kairos-folder-audit</a> · MIT License
</div>
</body>
</html>
"""


def render_html(results: dict, root: Path, cfg: dict, lang: str = "en") -> str:
    L = LOCALES.get(lang, LOCALES["en"])
    p0 = sum(len(r["findings"]) for r in results.values() if r["sev"] == "P0")
    p1 = sum(len(r["findings"]) for r in results.values() if r["sev"] == "P1")
    p2 = sum(len(r["findings"]) for r in results.values() if r["sev"] == "P2")
    p3 = sum(len(r["findings"]) for r in results.values() if r["sev"] == "P3")
    clean = sum(1 for r in results.values() if not r["findings"])
    total = p0 + p1 + p2 + p3

    parts = []
    for rule in cfg["rules"]:
        rid = rule["id"]
        if rid not in results:
            continue
        r = results[rid]
        fs = r["findings"]
        sev_lo = r["sev"].lower()
        if not fs:
            parts.append(f"""<div class="rule"><div class="rule-h"><div><span class="rule-id">{rid}</span> <span class="sev {sev_lo}">{r["sev"]}</span> {escape(r["title"])}</div><div class="count">{L["lab_clean"]}</div></div><div class="clean">{L["lab_passed"]}</div></div>""")
            continue
        f_html = "".join(
            f'<div class="f"><div class="f-path">{escape(f["path"])}</div>'
            f'<div class="f-msg">{escape(f["msg"])}</div>'
            f'<div class="f-action">→ {escape(f["action"])}</div></div>'
            for f in fs
        )
        count_label = L["lab_finding"] if len(fs) == 1 else L["lab_findings"]
        if lang == "ko":
            count_str = f'{len(fs)}{count_label}'
        else:
            count_str = f'{len(fs)} {count_label}'
        parts.append(f"""<div class="rule"><div class="rule-h"><div><span class="rule-id">{rid}</span> <span class="sev {sev_lo}">{r["sev"]}</span> {escape(r["title"])}</div><div class="count">{count_str}</div></div><div class="findings">{f_html}</div></div>""")
    return HTML_TEMPLATE.format(
        NOW=NOW_LABEL, ROOT=str(root),
        P0=p0, P1=p1, P2=p2, P3=p3, CLEAN=clean, TOTAL=total,
        L_TITLE=L["report_title"],
        L_P0=L["stat_p0"], L_P1=L["stat_p1"], L_P2=L["stat_p2"], L_P3=L["stat_p3"],
        L_CLEAN=L["stat_clean"], L_TOTAL=L["stat_total"],
        RULES_HTML="\n".join(parts),
    )


def print_cli(results: dict, cfg: dict, lang: str = "en") -> None:
    L = LOCALES.get(lang, LOCALES["en"])
    print()
    print(L["cli_header"].format(now=NOW_LABEL))
    print()
    total = 0
    for rule in cfg["rules"]:
        rid = rule["id"]
        if rid not in results:
            continue
        r = results[rid]
        if not r["findings"]:
            print(f"  ✓ {rid} [{r['sev']}] {r['title']}")
            continue
        n = len(r["findings"])
        unit = L["lab_finding"] if n == 1 else L["lab_findings"]
        sep = "" if lang == "ko" else " "
        print(f"  ⚠ {rid} [{r['sev']}] {r['title']}  ({n}{sep}{unit})")
        for f in r["findings"][:5]:
            print(f"      · {f['path']}: {f['msg']}")
        if n > 5:
            print(L["cli_more"].format(n=n - 5))
        total += n
    print()
    print(L["cli_total"].format(n=total))
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description="Folder hygiene health-check (10 configurable rules)")
    ap.add_argument("--path", type=Path, default=Path.cwd(), help="Path to audit (default: cwd)")
    ap.add_argument("--rules", type=Path, default=None, help="Custom rules.yml (default: built-in)")
    ap.add_argument("--lang", choices=["auto", "en", "ko"], default="auto",
                    help="Output language: auto (from $LANG) / en / ko (default: auto)")
    ap.add_argument("--quick", action="store_true", help="Quick mode: R01/R02/R04 only")
    ap.add_argument("--severity", choices=["p0", "p1", "p2", "p3"], help="Filter by severity")
    ap.add_argument("--out", type=Path, default=None, help="HTML output path (default: ./folder-audit-report.html)")
    ap.add_argument("--no-html", action="store_true", help="Skip HTML, CLI only")
    ap.add_argument("--no-cli", action="store_true", help="Skip CLI, HTML only")
    ap.add_argument("--no-open", action="store_true", help="Don't auto-open HTML in browser")
    args = ap.parse_args()

    lang = detect_lang() if args.lang == "auto" else args.lang

    root = args.path.expanduser().resolve()
    if not root.exists():
        print(f"❌ Path not found: {root}", file=sys.stderr)
        sys.exit(1)

    cfg = load_config(args.rules, lang=lang)
    results = run_all_rules(root, cfg, quick=args.quick, severity_filter=args.severity)
    L = LOCALES.get(lang, LOCALES["en"])

    out: Path | None = None
    if not args.no_html:
        out = args.out or (Path.cwd() / "folder-audit-report.html")
        html = render_html(results, root, cfg, lang=lang)
        out.write_text(html, encoding="utf-8")
        print(L["cli_html"].format(path=out))
        print(L["cli_open"].format(path=out))

    if not args.no_cli:
        print_cli(results, cfg, lang=lang)

    # Auto-open browser (default ON, --no-open to disable)
    if out is not None and not args.no_open:
        open_in_browser(out)

    p0 = sum(len(r["findings"]) for r in results.values() if r["sev"] == "P0")
    p1 = sum(len(r["findings"]) for r in results.values() if r["sev"] == "P1")
    if p0 > 0:
        sys.exit(1)
    if p1 > 0:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
