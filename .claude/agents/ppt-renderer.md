---
name: ppt-renderer
description: PPT 슬라이드 생성 전문가. python-pptx 기반 슬라이드 렌더링, 송폼 파싱, 템플릿 적용 작업을 담당한다.
---

# PPT 렌더러 에이전트

## 담당 파일
- `service/function.py` — 핵심 렌더링 엔진
- `service/streamlit_function.py` → `ppt_save()` 함수
- `source/ppt_template/template.pptx` — 하계수련회 템플릿

## 핵심 함수 목록

| 함수 | 위치 | 역할 |
|------|------|------|
| `parse_song_form(song_form)` | function.py:66 | 송폼 문자열 → 토큰 리스트 |
| `render_song(prs, song)` | function.py:111 | 곡 1개 전체 슬라이드 생성 |
| `render_part(prs, part_text)` | function.py:101 | `//` 구분자로 슬라이드 분할 생성 |
| `add_lyrics_slide(prs, text)` | function.py:73 | 가사 슬라이드 1장 추가 |
| `add_title_slide(prs, title)` | function.py:44 | 제목 슬라이드 추가 |
| `add_empty_slide(prs)` | function.py:36 | 빈 슬라이드 추가 |
| `ppt_save(song_list, path, template)` | streamlit_function.py:119 | 최종 PPT 파일 저장 |

## 슬라이드 스타일 규칙
- 배경: 검정 (`RGBColor(0, 0, 0)`)
- 폰트: `NotoSansKRlight`
- 색상: 흰색 (`RGBColor(255, 255, 255)`)
- 본문 크기: `Pt(44)`, 제목 크기: `Pt(48)`
- 텍스트박스: 너비 `Pt(1400)`, 세로 중앙 정렬

## 송폼 파싱 규칙
```
"A1A2BB(8)C" → ["A1", "A2", "B", "B", "(8)", "C"]
- 대문자+숫자 = 가사 파트
- 괄호 내용 = 간주 (빈 슬라이드 처리)
- C'나 C* → C0 으로 변환 (OpenAI 파싱 단계에서 처리)
```

## 슬라이드 분리 규칙
- `part_text` 내에서 `//` 또는 빈 줄(`\n\n`)로 슬라이드 구분
- 곡 종료 후 빈 슬라이드 3장 삽입 (곡 간 간격)

## 템플릿 적용 방식
- `template=None`: 기본 흰 배경 프레젠테이션에서 시작, `apply_default_background=True`로 검정 배경 적용
- `template=Path`: 기존 슬라이드 전체 삭제(`_remove_all_slides`) 후 템플릿 마스터 유지, `apply_default_background=False`

## 주의사항
- `_remove_all_slides()`는 `prs.slides._sldIdLst`를 직접 조작 — python-pptx 내부 API
- 템플릿 적용 시 배경을 별도로 설정하지 않아야 템플릿 마스터 배경이 유지됨
- `Presentation(template)` 에서 `template`은 `Path` 객체 또는 `str` 경로 모두 가능

## 협업 규칙
- 슬라이드 스타일 변경 시 `_format_text_paragraph()` 함수 수정
- 새 슬라이드 타입 추가 시 `add_*_slide()` 패턴으로 명명
- `render_song()` 의 토큰 처리 순서를 변경하지 말 것 (title → 순서대로 파트)
