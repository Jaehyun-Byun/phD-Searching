# PhD Job Search Agent — 작업 지침

이 파일은 매일/매주 실행되는 클라우드 에이전트가 따르는 지침이다. 사용자는 이 파일과
`profile.md`를 수정해서 에이전트의 행동을 바꿀 수 있다 (루틴 자체를 바꿀 필요 없음).

## 대상

- **사람**: 박사 학위 취득(예정)자, 구직 중. 세부 관심사는 `profile.md` 참고.
- **분야**: HCI, Design(인터랙션/UX/산업디자인/디자인 리서치), Computer Science
  (HCI·AI·시각화·소셜컴퓨팅 등 HCI와 겹치는 영역 우선).
- **포지션 종류** (`position_type` 값):
  - `Faculty` — Assistant/Associate Professor, Lecturer, Tenure-track, 조교수, 교원초빙
  - `Postdoc` — Postdoc, Research Fellow, 박사후연구원, 연구교수, 출연연 선임연구원
  - `Industry Research` — Research Scientist, UX Researcher, Research Engineer (기업 연구소)
  - `Industry` — Product/UX Designer, Design Technologist, Software Engineer 등 박사 우대 직무
- **지역** (`region` 값 — 반드시 이 5개 중 하나):
  - `Korea` — 대한민국
  - `Europe` — EU, 영국, 스위스, 노르웨이 등 유럽 전역
  - `USA` — 미국
  - `Asia` — 한국 제외 아시아 (일본, 중국, 홍콩, 대만, 싱가포르, 인도 등)
  - `Other` — 캐나다, 호주, 뉴질랜드, 중동(KAUST, MBZUAI 등), 남미, 아프리카, 원격

## 검색 소스 (매일 지역별로 최소 몇 곳씩 돌아가며 확인)

| 지역 | 소스 |
|---|---|
| Korea | hibrain.net(하이브레인넷), 각 대학 교원초빙 공고(KAIST·서울대·연세대·고려대·POSTECH·UNIST·GIST·DGIST·성균관대·한양대·홍익대 디자인 등), 출연연(KIST·ETRI·KISTI), 기업 채용(삼성리서치·네이버·카카오·LG AI연구원·현대차), 원티드, 사람인 |
| USA | CRA job ads (cra.org/ads), ACM Career Center (jobs.acm.org), Chronicle of Higher Education jobs, HigherEdJobs, Academic Jobs Online, SIGCHI jobs, 기업 연구소(Google, Meta, Microsoft Research, Apple, Adobe Research, Autodesk Research, Toyota Research Institute) |
| Europe | EURAXESS, jobs.ac.uk, AcademicPositions.net, AcademicTransfer(NL), ETH/EPFL jobs, Aalto, TU Delft, KTH, DTU, Max Planck, Inria, Design Research Society(DRS) jobs |
| Asia | NUS/NTU/SUTD careers, HKUST/HKU/CityU, JREC-IN(일본), 도쿄대/교토대, A*STAR, Times Higher Education jobs, 기업 연구소(Sony, NTT, Huawei, Microsoft Research Asia) |
| Other | University Affairs(캐나다), CAUT, Seek/대학 채용(호주), KAUST, MBZUAI |
| 공통 | LinkedIn jobs, jobRxiv, CHI/CSCW/UIST 관련 메일링리스트 공개 아카이브, X/블로그에 공유된 HCI faculty job 목록 |

검색어 예시: `"assistant professor" HCI 2027`, `"human-computer interaction" faculty position`,
`interaction design lecturer`, `postdoc HCI`, `"UX researcher" PhD`, `research scientist HCI`,
`조교수 초빙 디자인`, `교원 초빙 HCI`, `박사후연구원 인간컴퓨터상호작용`.

## 포함/제외 규칙

- 포함: 마감일이 오늘 이후이거나 rolling/미기재인 공고. 분야가 HCI/Design/CS와 명확히 관련.
- 제외: 학부·석사 학생 모집, 박사과정(PhD student) 모집, 인턴십, 마감 지난 공고,
  분야 무관(예: 순수 하드웨어/생물정보), 집계 사이트의 원 출처를 확인할 수 없는 의심 공고.
- **URL은 반드시 실제로 존재하는 공고 페이지**여야 한다. 추측해서 만들지 말 것. 확인 못 하면 넣지 말 것.
- 같은 공고가 여러 사이트에 있으면 원 출처(대학/기업 페이지) URL을 우선.

## 데이터 형식

새로 찾은 공고는 `data/inbox/YYYY-MM-DD.json` 에 JSON 배열로 저장한다 (날짜는 한국시간 기준 오늘):

```json
[
  {
    "title": "Assistant Professor in Human-Computer Interaction",
    "institution": "University of Example",
    "department": "School of Computer Science",
    "country": "United States",
    "region": "USA",
    "position_type": "Faculty",
    "field": "HCI; CS",
    "deadline": "2026-12-15",
    "url": "https://...",
    "source": "CRA",
    "summary": "한국어 1~2문장 요약 (연구 분야, 조건, 특이사항)",
    "fit": 3
  }
]
```

- `deadline`: `YYYY-MM-DD`, 또는 `rolling`, 또는 모르면 `""`.
- `fit`: `profile.md` 기준 적합도 1~3 (3=매우 적합). profile이 비어 있으면 `null`.
- 그 다음 `python scripts/merge.py data/inbox/YYYY-MM-DD.json` 실행 → `data/jobs.json`(마스터 DB)에
  중복 제거 후 병합되고 `data/jobs.csv`도 갱신된다. 이미 있는 공고를 다시 넣어도 괜찮다(중복은 자동 제거).

## 실행 모드

### DAILY (매일)
1. 아래 "Git 규칙"대로 데이터 브랜치를 체크아웃한다.
2. `data/jobs.json`을 훑어 이미 수집된 공고를 파악한다.
3. 5개 지역 모두에 대해 검색한다. 하루에 최소 15~25회 정도 검색/페이지 확인. 매일 같은 쿼리만
   반복하지 말고 소스 표를 돌아가며 사용한다.
4. 새 공고를 inbox JSON으로 저장 → merge.py 실행.
5. `data/daily/YYYY-MM-DD.md`에 짧은 로그: 확인한 소스, 신규 건수(지역별), 특이사항.
6. 커밋 & 푸시.

### WEEKLY (매주 일요일)
1. DAILY 1~5단계를 그대로 수행한다.
2. `python scripts/build_report.py` 실행 → `reports/YYYY-Www.md`, `reports/YYYY-Www.xlsx` 생성.
3. 생성된 md 파일 맨 위 `## 이번 주 요약` 아래에 3~6줄의 한국어 코멘트를 추가한다
   (눈에 띄는 공고, 마감 임박 건, 지역별 동향). 표는 수정하지 말 것.
4. `README.md`의 "최신 리포트" 링크를 이번 주 파일로 갱신.
5. 커밋 & 푸시.

## Git 규칙

- 데이터는 항상 `claude/job-data` 브랜치에 쌓는다.
  ```bash
  git fetch origin
  git checkout claude/job-data 2>/dev/null || git checkout -b claude/job-data
  git pull --ff-only origin claude/job-data 2>/dev/null || true
  git merge origin/main --no-edit -X theirs   # 사용자가 main에서 고친 AGENT.md/profile.md/scripts 반영
  ```
  merge 후 `AGENT.md`가 바뀌었으면 다시 읽고 새 지침을 따른다.
- 커밋 메시지: `daily: YYYY-MM-DD (+N new)` 또는 `weekly: YYYY-Www report`.
- `git push -u origin claude/job-data`. 실패하면 한 번 `git pull --rebase` 후 재시도.
- `main` 브랜치는 건드리지 않는다. PR을 만들지 않는다.
