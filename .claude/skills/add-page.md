---
name: add-page
description: 새 Streamlit 페이지를 추가할 때의 체크리스트. 파일 생성부터 사이드바 등록까지 단계별 가이드를 제공한다.
---

# 새 페이지 추가 체크리스트

## 1. 페이지 파일 생성

```bash
# pages/ 폴더에 번호_이름.py 형식으로 생성
# 예: pages/6_new_feature.py
```

파일 기본 구조:
```python
import streamlit as st

st.set_page_config(
    page_title="페이지 제목",
    page_icon="🙏🏻",
    layout="wide",
)

st.title("📌 페이지 제목")
# 페이지 로직 작성
```

## 2. pages.toml 등록

`.streamlit/pages.toml` 에 항목 추가:

```toml
[[pages]]
path = "pages/6_new_feature.py"
name = "✨ 새 기능"
icon = "✨"
```

## 3. 서비스 레이어 분리 (필요 시)

로직이 복잡해지면 서비스 파일 분리:
- `service/new_feature_component.py` — UI 컴포넌트 (`render_*` 함수)
- `service/new_feature_session.py` — 세션 초기화 (`init_*_session` 함수)
- `service/streamlit_function.py` — 공통 유틸 추가

## 4. CLAUDE.md 업데이트

`CLAUDE.md`의 "페이지별 역할" 섹션에 새 페이지 추가.

## 5. agent/skill 업데이트

새 기능 유형에 따라:
- UI 컴포넌트 추가 → `.claude/agents/streamlit-ui.md` 컴포넌트 목록 갱신
- OpenAI API 추가 → `.claude/agents/openai-integration.md` 함수 목록 갱신
- 새 반복 워크플로우 → `.claude/skills/` 에 스킬 파일 추가

## 체크리스트 요약

- [ ] `pages/N_name.py` 파일 생성
- [ ] `st.set_page_config()` 호출 (페이지 최상단)
- [ ] `.streamlit/pages.toml` 에 항목 추가
- [ ] 서비스 레이어 분리 (로직이 100줄 이상이면)
- [ ] `CLAUDE.md` 업데이트
- [ ] `.claude/agents/` 또는 `.claude/skills/` 업데이트
