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

실행하면 `./folder-audit-report.html` 생성 + **브라우저 자동 오픈**. `$LANG`이 `ko_KR`이면 자동으로 한국어 출력.

자동 오픈 끄기: `--no-open`. 영어 강제: `--lang en`.

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

![report](./docs/report-dark-ko.png)

`$LANG`이 `ko_KR`이면 자동으로 한국어 출력. 또는 `--lang ko` 명시.

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

## 심각도 안내

- **P0 차단** — 즉시 수정. 보안 또는 데이터 손실 위험.
- **P1 액션** — 이번 주 안에 처리. 구조 무결성 / 빌드 영향.
- **P2 권고** — 이번 달 안에 처리. 유지보수성 / 명료성.
- **P3 안내** — 인지만. 급한 액션 X.
- **Clean** — 룰이 잡은 게 없음. 해당 영역 건강.

## 결과 받으면 무엇을 하나

리포트가 나오면, 정리는 프롬프트 한 줄로 끝나요.

**Claude Code / Cursor / 다른 AI 에이전트와** — 추천 흐름:

1. `folder-audit` 실행 (CLI 출력이 터미널에 남음)
2. CLI 출력 복사, 또는 HTML 리포트를 AI 세션에 드래그
3. 프롬프트: _"P0와 P1 finding 수정해줘. 변경 전에 각각 보여주고."_
4. 검토 → 승인 → 끝.

이게 전체 루프예요. **Audit → AI → 정리.** 명령어 하나하나 직접 칠 필요 없음.

**또는 직접 정리** 하고 싶으면:

- **P0** → 즉시 (보안 / 데이터 리스크)
- **P1** → 이번 주 안에 (구조)
- **P2 / P3** → 다음 일요일 cron에 일괄

룰별 빠른 명령:

- **R01 빈 폴더** → `rmdir <경로>/`, 의도된 거면 `.gitkeep` 박제
- **R03 README 없음** → 1줄 `README.md` 추가, 또는 `rules.yml`의 `standard_child` 화이트리스트
- **R04 중복** → 1개 권위본 + 나머지 `git rm`
- **R05 misplaced `.md`** → `git mv <파일> reports/<파일>`
- **R10 `.env` 노출** → `echo ".env" >> .gitignore && git rm --cached .env`

진짜 가치: 아래 [일요일 cron](#매주-일요일-자동) 설정. audit이 자기가 매주 돌고, AI에 paste하면 정리가 끝납니다. 챙길 게 없어집니다.

## 매주 일요일 자동

```cron
0 6 * * 0  folder-audit --path ~/projects --out ~/folder-audit.html
```

한 번 세팅하면 끝. 매주 일요일 06시에 데스크탑에 리포트가 떨어집니다. 직접 챙길 필요 없음.

## 라이센스

[MIT](./LICENSE) © 2026 Sunny Lee

—

[@sun.young.0207](https://instagram.com/sun.young.0207) — Instagram · [Threads](https://threads.net/@sun.young.0207)
