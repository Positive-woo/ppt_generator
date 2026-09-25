# 동부교회 청년부 자막 생성기 — Claude Project Map

> 이 파일은 새 세션을 열 때마다 Claude가 프로젝트 전체를 즉시 파악할 수 있도록 작성된 맵입니다.

---

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 목적 | 교회 주일/수련회 예배 시 사용할 PPT 자막 슬라이드 자동 생성 |
| 기술 스택 | Python, Streamlit, python-pptx, OpenAI API, Bugs.co.kr 크롤링 |
| 실행 방법 | `streamlit run app.py` (포트 기본값 8501) 또는 `./run.command` |
| Python 버전 | `.python-version` 기준, uv로 venv 관리 |

---

## 디렉토리 구조

```
worship_ppt/
├── app.py                          # 홈(대시보드) 페이지
├── pages/
│   ├── 1_auto_maker.py             # 악보 이미지 → 자동 분석 → 가사 채우기
│   ├── 2_ppt_generator.py          # dict 입력 → PPT 파일 생성 및 다운로드
│   ├── 3_search_lyrics.py          # Bugs 가사 검색 → 파트 분리 → 텍스트 추출
│   ├── 4_video_preprocessing.py    # (미사용 stub)
│   └── 5_youtube_bpm_code.py       # YouTube URL → BPM/Key 분석
├── service/
│   ├── function.py                 # PPT 렌더링 핵심 로직 (슬라이드 생성, 송폼 파싱)
│   ├── openai_function.py          # OpenAI Vision/Text API 호출
│   ├── streamlit_function.py       # 공통 유틸: CSS 로드, 가사 크롤링, PPT 저장
│   ├── auto_maker_component.py     # auto_maker 페이지 UI 컴포넌트
│   ├── auto_maker_session.py       # auto_maker 세션 상태 초기화/관리
│   └── search_lyrics_component.py  # search_lyrics 페이지 UI 컴포넌트
├── source/
│   ├── lyrics.py / lyrics copy 2.py / day_3_lyrics.py  # 하드코딩된 가사 데이터
│   ├── ppt_template/template.pptx  # 하계수련회용 PPT 템플릿
│   └── dashboard.jpeg              # 홈 화면 이미지
├── css/
│   └── wide.css                    # 전체 레이아웃 확장 CSS
├── PPT/                            # 생성된 PPT 출력 폴더
├── .streamlit/
│   ├── config.toml                 # Streamlit 설정
│   └── pages.toml                  # 사이드바 페이지 순서/이름 정의
├── .claude/
│   ├── agents/                     # 역할별 전문 에이전트 정의
│   └── skills/                     # 재사용 워크플로우 스킬 정의
├── pyproject.toml / requirements.txt / uv.lock
└── .env                            # OPENAI_API_KEY 등 환경변수
```

---

## 페이지별 역할

### `app.py` — 홈
- 대시보드 이미지 표시, 앱 제목 렌더링
- 별도 로직 없음

### `pages/1_auto_maker.py` — 악보 자동 분석기
**흐름:** PDF/이미지 업로드 → OpenAI Vision으로 악보 파싱 → 곡 선택 → Bugs 가사 검색 → OpenAI로 파트 자동 채우기 → 주일예배용 텍스트 생성

핵심 세션 키:
- `auto_maker_result` — OpenAI 파싱 결과 `{song_1: [{song_name, song_form, A, B, ...}]}`
- `auto_maker_selected_song` — 선택된 곡 dict
- `auto_maker_lyrics_text` — Bugs에서 가져온 전체 가사
- `auto_maker_autofill_result` — OpenAI autofill 결과
- `auto_maker_sunday_preview_text` — 최종 주일예배용 텍스트

### `pages/2_ppt_generator.py` — PPT 생성기
**흐름:** 텍스트 영역에 song dict 붙여넣기 → PPT 생성 → 기본/하계 PPT 다운로드

입력 형식:
```python
[
  {
    "title": "곡 제목",
    "parts": {"A": "가사...", "B": "가사..."},
    "song_form": "AABBA",
  }
]
```

### `pages/3_search_lyrics.py` — 가사 검색기
**흐름:** Bugs.co.kr 검색 → 곡 선택 → 가사 자동 로드 → 파트 분리 입력 → 주일용(holiday) 또는 수련회용(retreat) 포맷으로 추출

### `pages/5_youtube_bpm_code.py` — BPM/Key 분석기
- YouTube URL → yt-dlp로 오디오 다운로드 → librosa로 BPM/Key 분석
- 로컬 전용 (웹 배포 불가, ffmpeg 필요)

---

## 서비스 레이어

### `service/function.py` — PPT 렌더링 엔진
| 함수 | 역할 |
|------|------|
| `parse_song_form(song_form)` | `"AABB(8)C"` → `["A","A","B","B","(8)","C"]` |
| `render_song(prs, song)` | 곡 1개 전체 슬라이드 생성 |
| `add_lyrics_slide(prs, text)` | 가사 슬라이드 1장 추가 |
| `add_title_slide(prs, title)` | 제목 슬라이드 추가 |
| `add_empty_slide(prs)` | 빈 슬라이드 추가 (간주/곡 구분) |
| `render_part(prs, part_text)` | `//` 구분자로 슬라이드 분할 |

슬라이드 스타일: 검은 배경 / 흰색 NotoSansKRlight 폰트 / Pt(44) 본문, Pt(48) 제목

### `service/openai_function.py` — OpenAI 연동
- `ask_openai_json(images_base64)`: Vision API로 악보 이미지 → `{song_1: [...]}` JSON 반환
- `request_openai_autofill(selected_song, full_lyrics)`: 가사 전문 → 파트별 가사 매핑 JSON 반환
- 모델: `gpt-5-mini` (vision + JSON response_format)

### `service/streamlit_function.py` — 공통 유틸
- `crawl_lyrics(song_name)`: Bugs.co.kr 검색 → `[{track_id, title, artist}]`
- `crawl_track_lyrics(track_id)`: 특정 트랙 가사 크롤링
- `ppt_save(song_list, path, template)`: PPT 파일 저장 (템플릿 지정 시 기존 슬라이드 제거 후 적용)
- `export_holiday/export_retreat`: 세션 파트 → 텍스트 포맷 추출
- `build_sunday_text(song_form, parts, title)`: 주일예배용 연속 텍스트 생성

---

## 핵심 데이터 포맷

### 송폼 (song_form)
```
"A1A2BB(8)A1A2BBC"
- 대문자+숫자: 가사 파트 (A, A1, A2, B, C ...)
- 괄호: 간주 마디 수 (8), (16) — 빈 슬라이드로 처리
- C'나 C* → C0 으로 변환
```

### 곡 dict (PPT 생성기 입력)
```python
{
  "title": "곡 제목",          # 선택, 없으면 제목 슬라이드 생략
  "parts": {
    "A": "가사 줄1\n가사 줄2\n\n다음 슬라이드\n...",  # // 또는 빈줄로 슬라이드 분리
    "B": "....",
  },
  "song_form": "AABBA",
}
```

---

## 환경 변수

| 변수 | 용도 |
|------|------|
| `OPENAI_API_KEY` | OpenAI Vision/Text API 인증 |

---

## 실행 명령

```bash
# 개발 서버 시작 (포트 8502)
streamlit run app.py --server.port 8502

# 기존 포트 점유 프로세스 종료
kill $(lsof -t -i :8502)

# 쉘 스크립트로 실행
./run.command
```

---

## .claude 에이전트/스킬 구조

```
.claude/
├── agents/
│   ├── ppt-renderer.md         # PPT 슬라이드 생성 전문가
│   ├── openai-integration.md   # OpenAI API 연동 전문가
│   ├── lyrics-assistant.md     # 가사 크롤링/파트 분리 전문가
│   └── streamlit-ui.md         # Streamlit UI 컴포넌트 전문가
└── skills/
    ├── run-app.md              # 앱 실행 스킬
    ├── add-page.md             # 새 페이지 추가 체크리스트
    └── update-agents-skills.md # 에이전트/스킬 업데이트 파이프라인
```

---

## 에이전트/스킬 업데이트 파이프라인

> **목표**: 대화를 통해 새로 파악된 패턴, 규칙, 결정 사항을 `.claude/agents`와 `.claude/skills`에 반영하여 다음 세션부터 즉시 활용 가능하게 유지한다.

### 업데이트 트리거 조건

| 상황 | 업데이트 대상 |
|------|-------------|
| 새로운 서비스 로직이 추가됨 | 관련 agent 파일의 함수 목록/흐름 갱신 |
| OpenAI 프롬프트가 수정됨 | `openai-integration.md` 프롬프트 규칙 갱신 |
| 새 Streamlit 페이지 추가됨 | `add-page.md` 체크리스트 + `streamlit-ui.md` 컴포넌트 목록 갱신 |
| 새로운 반복 작업 패턴 발견 | `.claude/skills/` 에 새 스킬 파일 추가 |
| 버그 수정 후 재발 방지 규칙 생김 | 해당 agent의 `## 주의사항` 섹션 갱신 |
| 사용자가 선호/기피 방식을 명시함 | 해당 agent의 `## 협업 규칙` 섹션 갱신 |

### 업데이트 절차

```
1. 대화 중 업데이트 필요 시점 감지
2. 해당 .claude/agents/*.md 또는 .claude/skills/*.md 파일을 Edit 툴로 수정
3. 변경 내용을 CLAUDE.md 관련 섹션에도 반영 (필요 시)
4. 세션 종료 전 memory 시스템에도 요약 저장 (user/feedback/project 타입)
```

### 정기 리뷰 체크리스트

세션 시작 시 아래를 확인하여 stale 항목 업데이트:
- [ ] `service/function.py`의 함수 목록이 `ppt-renderer.md`와 일치하는가?
- [ ] OpenAI 모델명이 `openai-integration.md`에 정확히 기재되어 있는가?
- [ ] `pages.toml`의 페이지 목록이 실제 `pages/` 파일과 일치하는가?
- [ ] 새로 추가된 세션 키가 이 CLAUDE.md에 반영되어 있는가?
