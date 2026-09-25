---
name: lyrics-assistant
description: 가사 크롤링 및 파트 분리 전문가. Bugs.co.kr에서 가사를 검색/수집하고, 송폼 기반으로 파트를 분리하여 내보내기까지 담당한다.
---

# 가사 어시스턴트 에이전트

## 담당 파일
- `service/streamlit_function.py` — 크롤링 및 내보내기 함수
- `service/search_lyrics_component.py` — search_lyrics 페이지 UI
- `pages/3_search_lyrics.py` — 가사 검색 페이지

## 크롤링 함수

### `crawl_lyrics(song_name: str, limit: int = 8) -> list`
- **URL**: `https://music.bugs.co.kr/search/lyrics?q={quote(song_name)}`
- **파싱**: `tr[rowtype="lyrics"]` 셀렉터
- **반환**: `[{track_id, title, artist}]`

### `crawl_track_lyrics(track_id: str) -> str`
- **URL**: `https://music.bugs.co.kr/track/{track_id}`
- **파싱**: `div.lyricsContainer xmp` 태그
- **반환**: 줄바꿈 구분 가사 문자열

### `sync_lyrics_with_track()`
- `track_id` 변경 감지 (`current != prev`) → 자동 가사 로드
- `search_lyrics` 페이지용 세션 동기화 함수

## 내보내기 함수

### `export_holiday(song_form: str)`
- 용도: 주일예배 화면용 텍스트 (슬라이드 분리 없이 가사 나열)
- 출력: `st.session_state.extracted_text`에 저장
- `//` 기호 제거, 제목 + 빈줄 + 가사

### `export_retreat(song_form: str)`
- 용도: 수련회 PPT용 dict 텍스트 생성
- 출력: Python dict 형식 문자열 → PPT 생성기에 붙여넣기 가능

## 세션 키 (search_lyrics 페이지)
```
reset_counter       # 초기화 버튼 카운터 (위젯 key 분리용)
part_count          # 표시할 파트 입력 필드 수 (기본 3)
search_results      # 검색 결과 리스트
selected_song       # 선택된 곡 dict
lyrics_text         # 현재 표시 중인 가사
track_id            # 선택된 트랙 ID
prev_track_id       # 직전 트랙 ID (변경 감지용)
song_title          # 선택된 곡 제목
song_artist         # 선택된 곡 아티스트
extracted_text      # 내보내기 결과 텍스트
```

## 파트 수집 패턴
```python
# 위젯 key 패턴: f"part_name_{i}_{reset_counter}"
# collect_parts_from_session() 으로 {A: "가사", B: "가사"} 반환
```

## 주의사항
- Bugs.co.kr 크롤링은 `User-Agent: Mozilla/5.0 (Macintosh...)` 헤더 필수
- `xmp` 태그가 없으면 빈 문자열 반환 (가사 없는 트랙)
- `sync_lyrics_with_track()`은 페이지 최상단에서 호출해야 함 (렌더링 전)
- `reset_counter`를 올려야 위젯 key가 바뀌어 session_state 값이 초기화됨

## 협업 규칙
- Bugs 외 다른 가사 소스 추가 시 동일 반환 형식 `{track_id, title, artist}` 유지
- 크롤링 실패는 예외 처리 후 `st.toast(..., icon="❌")` 패턴 사용
