# kairos-folder-audit

[English](./README.md) · **한국어**

> **한 줄 명령. 10가지 체크. 매주 자동. 폴더 걱정 끝.**

![demo](./docs/demo.gif)

## 설치

```bash
# 추천
pipx install git+https://github.com/sunyoung-lee/kairos-folder-audit.git

# uvx (설치 X)
uvx --from git+https://github.com/sunyoung-lee/kairos-folder-audit.git folder-audit

# 단일 파일 (제로 셋업)
curl -sSL https://raw.githubusercontent.com/sunyoung-lee/kairos-folder-audit/main/folder_audit.py -o folder_audit.py && python3 folder_audit.py
```

## 사용

```bash
folder-audit
```

`./folder-audit-report.html` 에 HTML 리포트가 생성됩니다 — 색상 코딩, 다크/라이트 토글, 공유 가능.

## 받는 가치

- **한 줄 명령**으로 전체 폴더 audit
- **HTML 리포트** — 저장·공유·나중에 다시 열기
- **매주 자동 실행** — 한 번 세팅, 다시 안 챙김
- **스트레스 0** — "6개월 전에 `.env` 커밋했나?" 다시는 안 떠올림

## 이런 분에게 좋아요

- 사이드 프로젝트 **5개 이상** 운영하는 1인 인디 메이커
- **Claude Code / Cursor**로 매일 AI 페어 코딩하는 개발자
- repo · 노션 · Drive에 **200개 이상 파일** 흩어진 분
- _"이 폴더 뭐였더라?"_ 자주 떠오르는 분

## 이런 상황에서 활용해요

- **일요일 아침** — 새 주 시작 전 가벼운 점검
- **새 프로젝트 시작 직전** — 기존 폴더 먼저 정리
- **6개월 누적 후** — 한 번에 통합 정리, 전체 상태 한눈에
- **repo public 공개 전** — `.env` 노출 / 중복 / 큰 파일 점검
- **AI 페어링 끝난 직후** — 잔여 파일·중복 노트 청소

## 리포트 예시

![report](./docs/report-dark.png)

## 10가지 체크

| ID  | Sev | 무엇을 잡는가                                  |
| --- | --- | --------------------------------------------- |
| R01 | P1  | 빈 폴더                                       |
| R02 | P2  | Dormant 폴더 (README만, 14일+ 변경 X)         |
| R03 | P2  | README 누락                                   |
| R04 | P1  | 중복 파일 (MD5)                               |
| R05 | P1  | Misplaced 루트 `.md` (YYYYMMDD-* 패턴)        |
| R06 | P2  | Experiments 슬러그 컨벤션                     |
| R07 | P2  | 거대 파일 (5MB+)                              |
| R08 | P1  | 화이트리스트 외 루트 파일                     |
| R09 | P3  | Untracked git 누적 (10건+)                    |
| R10 | P0  | `.env` 보호                                   |

P0 critical · P1 action · P2 advisory · P3 info.

## 매주 일요일 자동

```cron
0 6 * * 0  folder-audit --path ~/projects --out ~/folder-audit.html
```

한 번 세팅하면 끝. 매주 일요일 06시에 데스크탑에 리포트가 떨어집니다. 직접 챙길 필요 없음.

## 라이센스

[MIT](./LICENSE) © 2026 Sunny Lee

—

[@sun.young.0207](https://instagram.com/sun.young.0207) — Instagram · [Threads](https://threads.net/@sun.young.0207)
