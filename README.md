# PhD Job Search Agent

HCI · Design · CS 분야 박사 포지션(교수/포닥/산업계 연구/산업계)을 매일 자동 검색하고,
매주 일요일 지역별(한국/유럽/미국/아시아/그 외) 리포트를 만드는 Claude 클라우드 루틴.

- **최신 리포트**: (첫 주간 리포트 생성 후 자동 갱신)
- 결과는 `claude/job-data` 브랜치에 쌓입니다.

## 구조

| 경로 | 내용 |
|---|---|
| `AGENT.md` | 에이전트 작업 지침 (검색 소스, 포함/제외 규칙, 실행 절차) — 수정하면 다음 실행부터 반영 |
| `profile.md` | 내 연구 키워드/선호 조건 — 채우면 공고별 적합도(★) 표시 |
| `data/jobs.json`, `data/jobs.csv` | 누적 공고 DB (CSV는 Excel에서 바로 열림) |
| `data/daily/` | 일일 검색 로그 |
| `reports/YYYY-Www.md`, `.xlsx` | 주간 리포트 (Excel: 이번주 신규 / 마감 임박 / 지역별 시트) |

## PC로 받아보기

```bash
git clone -b claude/job-data <이 저장소 URL>
git pull
```

## 스케줄 (한국시간)

- 매일(월~토) 22:00 — 검색 & 누적
- 매주 일요일 22:00 — 검색 + 주간 리포트

`AGENT.md`, `profile.md`는 `main` 브랜치에서 수정하면 됩니다. 에이전트가 매 실행 시 `main`을 데이터 브랜치로 merge합니다.
