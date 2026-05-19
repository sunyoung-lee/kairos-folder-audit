# kairos-folder-audit

[English](./README.md) · **한국어**

> 일요일 아침 폴더 위생 게이트. 30개 이상 사이드 프로젝트 굴리는 메이커를 위한 도구.

![demo](./docs/demo.gif)

---

## 35개 repo 문제

어느 일요일 아침이었어요. 깃허브를 열다가, 제가 **35개 repo**를 운영하고 있다는 걸 새삼 확인했습니다. 사이드 프로젝트, K-Series 마이크로 SaaS, audit 도구, 콘텐츠 영상 — 다 살아있고, 다 다른 상태로요.

그러다 한 번도 안 해본 생각이 들었어요. _"#28번 repo는 마지막으로 언제 열었지?"_

전혀 기억이 안 났습니다.

폴더를 **측정**해본 적이 없었던 거예요. 정리야 가끔 했죠. 측정은 한 번도 안 해봤어요. 그래서 AI한테 시켰습니다.

10개 룰. 한 줄 명령. 첫 실행이 **40건**을 찾아냈습니다:
- 빈 폴더 4개 — 오래된 프로젝트에 그대로 남은 것
- README 없는 디렉토리 9개 — 뭐 하는 폴더인지 저도 까먹은 것
- 같은 노트의 중복 9건 — 3군데에 똑같이 박혀있던 것
- untracked 파일 16건 — git status에 조용히 쌓이던 것
- 잘못된 위치 markdown 2건 — 디렉토리 위치가 어긋난 것

5분 안에 18건 정리했어요. 나머지는 **advisory**로 박제 — 알고 있되 급하지 않은 것.

근데 진짜 가치는 정리 자체가 아니었습니다.

**일요일 06:00 cron으로 매주 자동 실행하게 해둔 것**이었어요. 그 시점부터, **다시는 모를 수가 없게** 됐어요.

검사를 자동화하면, 정리는 자연스럽게 따라옵니다.

이 도구가 그 결과물입니다.

---

## 어떻게 동작하나요 (짧은 버전)

```
1. 한 번 설치              →  pipx install kairos-folder-audit
2. 어디서든 실행            →  folder-audit
3. HTML 리포트 받기         →  10개 룰, 전체 폴더, 색상 코딩
4. (선택) 일요일 cron 등록  →  매주 자동 실행, 데스크탑에 리포트 박제
```

코드 직접 못 돌리셔도 괜찮습니다. **이 도구가 검사하는 10가지는 어떤 폴더 시스템이든 잘못될 수 있는 10가지**예요. 아래 ["이 audit이 잡는 10가지"](#이-audit이-잡는-10가지)를 직접 손으로 점검하는 체크리스트로 보셔도 됩니다.

---

## 이 도구가 **아닌 것**

기대치 정렬:

- ❌ **코드 린터 아님** — [Ruff](https://github.com/astral-sh/ruff) 쓰세요
- ❌ **시크릿 스캐너 아님** — [Gitleaks](https://github.com/gitleaks/gitleaks) 쓰세요
- ❌ **OSPO 컴플라이언스 도구 아님** — [repolinter](https://github.com/todogroup/repolinter) (RIP, 2026-02 archived)
- ❌ **파일 자동 이동기 아님** — [organize](https://github.com/tfeldmann/organize) 쓰세요
- ✅ **맞는 것:** 너무 많은 사이드 프로젝트를 굴리는 1인 메이커를 위한 주간 위생 게이트.

---

## 설치

```bash
# 권장 — pipx (isolated, auto-update)
pipx install kairos-folder-audit

# 빠르고 모던한 방법
uvx kairos-folder-audit

# 제로 셋업 단일 파일 (패키지 설치 X)
curl -sSL https://raw.githubusercontent.com/sunyoung-lee/kairos-folder-audit/main/folder_audit.py \
  -o folder_audit.py && python3 folder_audit.py
```

Python 3.10+ 필요. PyYAML은 옵션 (커스텀 `rules.yml` 쓸 때만).

## Quick start

```bash
# 현재 폴더 audit
folder-audit

# 다른 경로 audit
folder-audit --path ~/projects

# 가장 critical한 룰만 (빠름)
folder-audit --quick

# HTML 생략, CLI 출력만
folder-audit --no-html
```

HTML 리포트는 `./folder-audit-report.html`에 생성됩니다. 브라우저에서 열면 됩니다 — 모서리에 다크/라이트 토글 있어요.

CI에 쓸 때 exit codes: `0` clean · `1` critical 발견 (P0) · `2` action item 발견 (P1).

---

## 이 audit이 잡는 10가지

도구를 설치하지 않더라도, 이 리스트 자체가 가치입니다. 폴더 시스템이 조용히 무너지는 10가지 방식:

| ID  | Sev | 무엇을 잡는가                                  | 흔한 사연                                                        |
| --- | --- | --------------------------------------------- | ---------------------------------------------------------------- |
| R01 | P1  | **빈 폴더** — 파일 0개, 하위 0개               | "2023년에 만들고 한 번도 안 쓴 폴더"                            |
| R02 | P2  | **Dormant 폴더** — README만, 14일+ 변경 없음   | "시작해서 README만 쓰고 방치한 프로젝트"                        |
| R03 | P2  | **README 누락**                                | "이 폴더 뭐 하던 거였지? 저도 기억 안 남"                       |
| R04 | P1  | **중복 파일** — MD5 해시 충돌                  | "왜 `notes.md`가 3군데에 똑같이 박혀있지?"                      |
| R05 | P1  | **Misplaced 루트 `.md`** — YYYYMMDD-* 패턴     | "데일리 노트가 프로젝트 루트에 흩어짐"                          |
| R06 | P2  | **슬러그 컨벤션** — `experiments/<slug>-<NN>`  | "정렬 안 되는 랜덤 이름의 실험 폴더"                            |
| R07 | P2  | **거대 파일** — 5MB+, `output/` `input/` 제외  | "300MB asset이 git에 박혀있는 줄 몰랐음"                        |
| R08 | P1  | **화이트리스트 외 루트 파일**                  | "repo 루트에 랜덤 `.zip` 파일"                                  |
| R09 | P3  | **Untracked git 누적** — 10건+                 | "git status가 더 이상 읽을 수 없는 상태"                        |
| R10 | P0  | **`.env` 보호** — gitignore 커버리지           | "잠깐, 6개월 전에 API 키 커밋한 거 아니지?"                     |

Severity 범례: **P0** critical · **P1** action · **P2** advisory · **P3** info.

---

## 설정

모든 룰은 `rules.yml`에 외부화돼 있습니다. 스크립트 옆에 복사하고, 편집하고, `--rules rules.yml` 전달:

```yaml
rules:
  - id: R02
    severity: P2
    title: "Dormant folders"
    enabled: true
    days_threshold: 21        # 14에서 21로 — 본인한테 여유 주기

  - id: R07
    severity: P2
    title: "Large files"
    enabled: false            # 이 repo에선 비활성화
    size_bytes: 5000000

exclude_dirs:
  - .git
  - node_modules
  - my-custom-skip

approved_root_files:
  - README.md
  - CHANGELOG.md
  - my-tool.config.json       # 본인 프로젝트 루트 파일 추가
```

커스텀 설정으로 실행:

```bash
folder-audit --rules ./rules.yml --path ~/projects
```

---

## 일요일 06:00 cron (제가 실제로 쓰는 방식)

한 번 돌려보는 audit은 호기심에 그칩니다. **매주 일요일 6시에 자동으로 도는 audit**이 습관을 바꿔요.

**macOS (launchd)**: `~/Library/LaunchAgents/com.user.folder-audit.plist`에 박제:

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

등록:

```bash
launchctl load ~/Library/LaunchAgents/com.user.folder-audit.plist
```

**Linux (crontab):**

```cron
0 6 * * 0  /usr/local/bin/folder-audit --path ~/projects --out ~/folder-audit.html
```

이제 일요일 아침에 책상 앞에 앉으면, 리포트가 이미 데스크탑에 있어요. 확인하는 걸 기억할 필요 없어요. 측정해버린 건 못 본 척할 수 없어요.

---

## 로드맵

외부 검증 기반 (전체 리서치: [research/20260519-deep-folder-audit-launch.md](https://github.com/sunyoung-lee/kairosai/blob/main/research/20260519-deep-folder-audit-launch.md)):

- **v0.2**
  - **R11** 시크릿 콘텐츠 스캔 (P0) — `.env`를 넘어서 `.md`·`.py`·`.json` 본문의 AWS key / private key / Slack webhook (Gitleaks 스타일 정규식)
  - **R12** 깨진 심볼릭 링크 (P2) — `find -xtype l` 동등
  - **R13** 대소문자 충돌 (P1) — macOS↔Linux 배포 안전성
  - CVSS/SonarQube 산업 표준 정합 severity 재매핑
- **v0.3**
  - `pre-commit` hook 통합
  - TODO/FIXME ownership 린트
  - JSON 출력 (CI 파이프라인용)

---

## 기여

단일 ~400 줄 파일입니다. fork·adapt 쉽습니다.

```bash
git clone https://github.com/sunyoung-lee/kairos-folder-audit
cd kairos-folder-audit
python3 folder_audit.py --path .
```

이슈와 PR 환영합니다.

## 라이센스

[MIT](./LICENSE) © 2026 Sunny Lee

---

## Background

[kairos](https://instagram.com/sun.young.0207) 도구 셋의 일부 — 35개 이상 사이드 프로젝트를 1인으로 굴리는 인디 메이커의 개인 하네스입니다.

이 시스템이 어떻게 돌아가는지 궁금하시거나, 빌드 과정을 보고 싶거나, 혼자서 이 정도 굴리는 게 실제로 어떤지 보고 싶으시면:

- 📷 Instagram — [@sun.young.0207](https://instagram.com/sun.young.0207)
- 🧵 Threads — [@sun.young.0207](https://threads.net/@sun.young.0207)

이 도구의 발사 영상이 거기에 먼저 올라갔어요.
