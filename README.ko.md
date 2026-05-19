# kairos-folder-audit

[English](./README.md) · **한국어**

> **10개 룰. 일요일 06시. HTML 리포트. 30개 이상 사이드 프로젝트 굴리는 메이커를 위한 도구.**

폴더 트리를 워크하면서 10개 설정 가능한 룰을 적용하고, 다크/라이트 토글이 있는 자체완결 HTML 리포트를 생성하는 CLI입니다. 핵심 검사는 의존성 0개 (Python 표준 라이브러리만).

[@sun.young.0207](https://instagram.com/sun.young.0207)가 "35개 repo 문제" — _"35개 GitHub repo 굴리는데, repo #28은 마지막으로 언제 열었지?"_ — 를 해결하려고 만들었습니다.

![Folder Audit Report 스크린샷 — 다크 모드](docs/screenshot-dark.png)

## 무엇이냐

**단일 파일 Python 스크립트**. 폴더 트리를 워크하고, 10개 룰 (빈 폴더 / dormant 폴더 / README 누락 / MD5 중복 / misplaced 루트 파일 / 슬러그 컨벤션 / 거대 파일 / 루트 화이트리스트 / untracked git 누적 / .env 보호)을 적용해서, 공유·박제·일요일 cron에 걸 수 있는 자체완결 HTML 리포트를 렌더링합니다.

## 무엇이 **아닌가**

- ❌ 코드 린터 아님 ([Ruff](https://github.com/astral-sh/ruff) 쓰세요)
- ❌ 시크릿 스캐너 아님 ([Gitleaks](https://github.com/gitleaks/gitleaks) 쓰세요)
- ❌ OSPO 컴플라이언스 도구 아님 ([repolinter](https://github.com/todogroup/repolinter) — RIP, 2026-02 archived)
- ❌ 파일 자동 이동기 아님 ([organize](https://github.com/tfeldmann/organize) 쓰세요)
- ✅ **30개 이상 repo 굴리는 인디 메이커를 위한 일요일 아침 폴더 위생 게이트.**

## 설치

```bash
# 권장 — pipx (isolated, auto-update)
pipx install kairos-folder-audit

# 대안 — uv (더 빠름, 모던)
uvx kairos-folder-audit

# 제로 셋업 — 단일 파일 curl (패키지 설치 X)
curl -sSL https://raw.githubusercontent.com/sunyoung-lee/kairos-folder-audit/main/folder_audit.py \
  -o folder_audit.py && python3 folder_audit.py
```

Python 3.10+ 필요. PyYAML은 옵션 (`rules.yml` 커스터마이즈할 때만).

## Quick start

```bash
# 현재 디렉토리 audit
folder-audit

# 특정 경로 audit
folder-audit --path ~/projects

# Quick 모드 (R01/R02/R04만)
folder-audit --quick

# CLI 출력만, HTML 생략
folder-audit --no-html

# Severity 필터
folder-audit --severity p0
```

HTML 리포트는 기본 `./folder-audit-report.html`에 생성됩니다. `--out path/to/report.html`로 변경 가능.

## 10개 룰

| ID  | Severity | 제목                                        | 무엇을 잡는가                                                |
| --- | -------- | ------------------------------------------- | ----------------------------------------------------------- |
| R01 | P1       | 빈 폴더                                     | 파일 0개 + 하위 디렉토리 0개                                |
| R02 | P2       | Dormant 폴더 (README-only, 14일+ 변경 없음) | 잊혀진 프로젝트: README 1개만 있고 다른 활동 없음           |
| R03 | P2       | 상위 폴더 README 누락                       | `README.md` 없는 상위 디렉토리 (화이트리스트 설정 가능)     |
| R04 | P1       | 중복 파일 (MD5 해시 충돌)                   | 트리 전체에서 동일 내용 텍스트 파일                         |
| R05 | P1       | Misplaced 루트 `*.md` (YYYYMMDD-* 패턴)     | 날짜-prefix 노트가 `reports/` 대신 repo 루트에 흩어짐       |
| R06 | P2       | Experiments 슬러그 컨벤션                   | `experiments/<slug>-<NN>` 강제 (설정 가능)                  |
| R07 | P2       | 거대 파일 (5MB+, `output/` `input/` 제외)   | 스토리지나 gitignore에 가야 할 바이너리                     |
| R08 | P1       | 화이트리스트 외 루트 파일                   | `approved_root_files`에 없는 repo 루트 파일                 |
| R09 | P3       | Untracked git 누적 (10건+)                  | git status 오염 리스크                                      |
| R10 | P0       | `.env` 보호 게이트                          | `.gitignore`로 보호되지 않는 `.env` 파일                    |

Severity 범례: **P0** critical · **P1** action · **P2** advisory · **P3** info.
Exit codes: `0` clean · `1` P0 발견 · `2` P1 발견 (P2/P3는 fail X).

## 설정

모든 룰은 `rules.yml`에 외부화되어 있습니다 — 스크립트 옆에 복사한 뒤 `--rules rules.yml` 전달:

```yaml
rules:
  - id: R02
    severity: P2
    title: "Dormant folders"
    enabled: true
    days_threshold: 21       # 14 → 21로 변경

  - id: R07
    severity: P2
    title: "Large files"
    enabled: false           # 이 repo에선 비활성화
    size_bytes: 5000000

exclude_dirs:
  - .git
  - node_modules
  - my-custom-skip

approved_root_files:
  - README.md
  - CHANGELOG.md
  - my-tool.config.json     # 본인 프로젝트의 루트 파일 추가
```

커스텀 설정으로 실행:

```bash
folder-audit --rules ./rules.yml --path ~/projects
```

## 일요일 06시 cron (macOS launchd)

제가 실제로 쓰는 방식. `~/Library/LaunchAgents/com.user.folder-audit.plist`에 박제:

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

`launchctl load ~/Library/LaunchAgents/com.user.folder-audit.plist`로 등록.

Linux는 crontab:

```cron
0 6 * * 0  /usr/local/bin/folder-audit --path ~/projects --out ~/folder-audit.html
```

## 왜 만들었나

이런 경험 있으셨다면:
- 사이드 프로젝트 어느 repo가 마지막이었는지 기억 안 남
- 같은 `notes.md`가 3개 폴더에 4번 복제됨
- 6개월 전에 커밋한 `.env` 파일 발견
- 300MB asset이 git에 박혀있는 걸 나중에 발견

…이게 네 가지 모두 커지기 전에 잡아내는 일요일 아침 게이트입니다.

## 로드맵 (v0.2+)

외부 검증 리서치 기반으로 향후 버전 계획:

- **R11** 시크릿 콘텐츠 스캔 (P0) — `.env`를 넘어서 `.md`·`.py`·`.json` 본문의 AWS key / private key / Slack webhook (Gitleaks 스타일 정규식)
- **R12** 깨진 심볼릭 링크 (P2) — `find -xtype l` 동등
- **R13** 대소문자 충돌 (P1) — macOS↔Linux 배포 안전성
- CVSS/SonarQube 산업 표준 정합 severity 재매핑 (R01→P3, R04→P2, R05→P2)
- TODO/FIXME ownership 린트
- `pre-commit` hook 통합

## 기여

이슈와 PR 환영합니다. 단일 파일 스크립트 (~400 줄) — fork·adapt 쉽습니다.

```bash
git clone https://github.com/sunyoung-lee/kairos-folder-audit
cd kairos-folder-audit
python3 folder_audit.py --path .   # dogfood
```

## 라이센스

[MIT](./LICENSE) © 2026 Sunny Lee

## Background

[kairos](https://instagram.com/sun.young.0207) 도구 셋의 일부 — 1인 인디 메이커로 35개 이상 사이드 프로젝트를 굴리는 개인 하네스. 더 큰 시스템이 궁금하거나 빌드 과정을 따라가고 싶으면 [Instagram](https://instagram.com/sun.young.0207)에서 프로세스 영상 확인하세요.
