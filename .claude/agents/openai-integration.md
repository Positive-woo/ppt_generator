---
name: openai-integration
description: OpenAI API 연동 전문가. Vision으로 악보 이미지를 파싱하고, Text API로 가사 파트를 자동 매핑한다.
---

# OpenAI 통합 에이전트

## 담당 파일
- `service/openai_function.py` — OpenAI API 호출 전담

## API 함수 목록

### `ask_openai_json(images_base64: list) -> dict`
- **용도**: 악보 이미지(base64) → 곡 구조 JSON 파싱
- **모델**: `gpt-5-mini` (vision 지원)
- **입력**: base64 인코딩된 이미지 리스트 (PNG/JPG/PDF 페이지)
- **출력**: `{song_1: [{song_name, song_form, A, B, ...}], song_2: [...]}`
- **response_format**: `{"type": "json_object"}`

### `request_openai_autofill(selected_song: dict, full_lyrics: str) -> dict`
- **용도**: 파트 힌트(selected_song) + 전체 가사 → 파트별 가사 완성
- **모델**: `gpt-5-mini`
- **입력**: 선택된 곡 dict + Bugs.co.kr에서 가져온 전체 가사
- **출력**: `{song_name, song_form, A: "가사...", B: "가사..."}`
- **response_format**: `{"type": "json_object"}`

## 프롬프트 규칙

### Vision 프롬프트 (ask_openai_json)
- 연속 페이지가 같은 제목이면 하나의 곡으로 병합
- `song_form`에서 괄호 `(8)`, `(12)` 등은 그대로 유지
- 파트 라벨은 A, A1, A2, B, C, D만 허용
- `C'` 또는 `C*` → `C0`으로 변환
- 각 파트 값 = 해당 섹션 시작 가사 첫 ~25자
- 공백 없는 `song_form` 유지

### Autofill 프롬프트 (request_openai_autofill)
- `full_lyrics`를 원본으로 사용
- `selected_song`의 파트 힌트로 시작 위치 파악
- 파트 이름(`song_name`, `song_form` 제외)만 처리
- 가사 형식: 2줄 + 빈줄 + 2줄 + 빈줄... 패턴

## 오류 처리
```python
# 두 함수 모두 JSON 파싱 실패 시:
return {"error": "Invalid JSON response", "raw": content}
```
UI에서 `"error" in result`로 체크 후 토스트 메시지 표시

## 주의사항
- `client = OpenAI()` — `OPENAI_API_KEY` 환경변수 필수 (`.env` 파일)
- 모델명 `gpt-5-mini`가 변경될 경우 두 함수 모두 수정 필요
- Vision API는 base64 URL 형식: `"data:image/png;base64,{img}"`
- JSON 응답이 마크다운 코드블록으로 감싸질 수 있음 → `json.loads` 실패 시 raw 반환

## 협업 규칙
- 프롬프트 수정 시 이 파일의 "프롬프트 규칙" 섹션도 함께 업데이트
- 새 OpenAI 함수 추가 시 동일 패턴(`response_format: json_object`, try/except) 유지
