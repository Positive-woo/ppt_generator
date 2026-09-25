---
name: run-app
description: 앱을 로컬에서 실행하는 스킬. 개발 서버 시작, 포트 충돌 해결, 로그 확인 방법을 제공한다.
---

# 앱 실행 스킬

## 기본 실행

```bash
# .venv 활성화 후 실행
source .venv/bin/activate
streamlit run app.py
```

## 포트 지정 실행

```bash
# 기본 포트(8501) 대신 8502 사용
streamlit run app.py --server.port 8502
```

## 포트 충돌 해결

```bash
# 8502 포트 점유 프로세스 종료
kill $(lsof -t -i :8502)
```

## 쉘 스크립트 실행

```bash
# run.command 파일 권한 부여 후 실행
chmod +x run.command
./run.command
```

## uv로 실행 (venv 없이)

```bash
uv run streamlit run app.py
```

## 확인 사항
- `.env` 파일에 `OPENAI_API_KEY` 설정 여부 확인
- `packages.txt` 에 시스템 패키지 목록 있음 (ffmpeg 등 로컬 설치 필요)
- YouTube BPM 분석 기능은 ffmpeg 설치 필요 (로컬 전용)
- Streamlit 설정은 `.streamlit/config.toml` 참조
