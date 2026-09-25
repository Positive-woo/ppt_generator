---
name: streamlit-ui
description: Streamlit UI 컴포넌트 전문가. 페이지 레이아웃, 세션 상태 관리, CSS 커스터마이징, 재사용 컴포넌트 작성을 담당한다.
---

# Streamlit UI 에이전트

## 담당 파일
- `service/auto_maker_component.py` — auto_maker 페이지 컴포넌트
- `service/search_lyrics_component.py` — search_lyrics 페이지 컴포넌트
- `service/auto_maker_session.py` — 세션 초기화
- `service/streamlit_function.py` → `load_css()`, `listup_lyrics_result()` 등
- `css/wide.css` — 전역 CSS
- `.streamlit/pages.toml` — 페이지 사이드바 설정

## 컴포넌트 구조 패턴

### 컴포넌트 파일 규칙
- `render_*()` — 화면 렌더링 함수
- `load_*_css()` — CSS 주입 함수
- 비즈니스 로직은 컴포넌트에서 배제 → `streamlit_function.py`로 위임

### auto_maker 컴포넌트 목록
| 함수 | 역할 |
|------|------|
| `upload_button()` | PDF/이미지 업로드 → base64 리스트 반환 |
| `load_song_grid_css()` | 곡 카드 그리드 CSS 주입 |
| `render_song_boxes(result)` | 곡 선택 카드 UI 렌더링 |
| `render_lyrics_tool_title()` | 섹션 제목 표시 |
| `render_lyrics_search_panel(crawl_fn, crawl_track_fn)` | 가사 검색 패널 |
| `render_lyrics_editor_header()` | 가사 편집 헤더 + 자동생성 버튼 |
| `render_lyrics_editor_text_area()` | 가사 입력 텍스트 영역 |
| `render_song_form_editor_panel()` | 송폼 + 파트 입력 패널 |
| `render_autofill_result_panel(result, preview)` | 자동생성 결과 표시 |

### search_lyrics 컴포넌트 목록
| 함수 | 역할 |
|------|------|
| `render_title_bar(reset_fn)` | 제목 + 초기화 버튼 |
| `render_search_column(crawl_fn, listup_fn)` | 가사 검색 패널 |
| `render_lyrics_column()` | 가사 표시 패널 |
| `render_song_form_column()` | 파트 입력 패널 |
| `render_export_actions(song_form, holiday_fn, retreat_fn)` | 내보내기 버튼들 |
| `render_extracted_result()` | 추출 결과 텍스트 표시 |

## 레이아웃 패턴
```python
# 표준 3컬럼 레이아웃 (검색/가사/폼)
col_left, col_center, col_right = st.columns([1.5, 1.3, 1.5])

# 표준 2컬럼 레이아웃
col_left, col_right = st.columns([3, 1])
```

## 세션 상태 관리 패턴

### 위젯 key 충돌 방지
```python
# reset_counter로 동적 key 생성 → 초기화 시 새 위젯 강제 생성
f"part_name_{i}_{reset_counter}"
f"part_lyrics_{i}_{reset_counter}"
```

### 세션 초기화 패턴
```python
# init_auto_maker_session() 패턴
defaults = {"key": default_value, ...}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value
```

## CSS 클래스 목록
```css
/* css/wide.css - 전역 */
.song-card-wrapper / .song-card / .song-title / .song-artist

/* auto_maker_component.py 인라인 CSS */
.song-grid          /* 그리드 레이아웃 */
.song-box           /* 곡 카드 컨테이너 */
.song-box-selected  /* 선택된 카드 강조 */
.section-row        /* 파트 행 */
.section-label      /* 파트 레이블 (A, B...) */
.section-content    /* 파트 가사 미리보기 */
```

## .streamlit/pages.toml 관리
```toml
[[pages]]
path = "app.py"
name = "🏠 Home"
icon = "🏠"

[[pages]]
path = "pages/1_auto_maker.py"   # 실제 파일명과 일치해야 함
name = "📂 악보 자동 분석"
```
- 새 페이지 추가 시 이 파일에 항목 추가 필수
- `path`는 실제 파일 경로, `name`은 사이드바 표시명

## 주의사항
- `st.rerun()` 호출 전 필요한 세션 값을 모두 설정해야 함
- `st.form()` 내부에서는 `st.button()` 대신 `st.form_submit_button()` 사용
- `unsafe_allow_html=True` 사용 시 `html.escape()`로 XSS 방지 필수
- PDF 업로드는 `pdf2image` 의존성 필요 (로컬 전용 기능)

## 협업 규칙
- 새 컴포넌트 추가 시 `render_` 접두사 + 단일 책임 원칙
- CSS는 가능하면 `wide.css`에, 컴포넌트 전용은 `load_*_css()` 내 인라인 주입
- 컴포넌트 함수 추가 시 이 파일의 컴포넌트 목록 업데이트
