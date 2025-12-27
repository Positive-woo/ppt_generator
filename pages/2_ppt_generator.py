from datetime import datetime
from service.streamlit_function import ppt_save
from io import BytesIO
import streamlit as st
import ast

st.set_page_config(
    page_title="수련회용 PPT 생성기",
    page_icon="🙏🏻",
    layout="wide",
)

st.title("💬 PPT 생성기")

# ----------------------
# Layout: 2 Columns
# ----------------------
col_left, col_right = st.columns([3, 1])

# ----------------------
# Left: Text Input
# ----------------------
with col_left:
    st.subheader("DICT형태의 곡 정보 첨부")

    ppt_text = st.text_area(
        label="",
        height=500,
        placeholder="여기에 PPT로 만들 텍스트를 붙여넣으세요",
        key="ppt_source_text",
    )
    if ppt_text.strip():
        try:
            song_list = ast.literal_eval(ppt_text)

            if not isinstance(song_list, list):
                raise ValueError("list 형식이 아닙니다.")

            for i, item in enumerate(song_list):
                if not isinstance(item, dict):
                    raise ValueError(f"{i}번째 요소가 dict가 아닙니다.")

            st.session_state.song_list = song_list
            st.toast(f"{len(song_list)}곡이 list로 저장되었습니다.", icon="✅")

        except Exception as e:
            st.toast(f"list 파싱 실패: {e}", icon="❌")

# ----------------------
# Right: Action Button
# ----------------------
with col_right:
    st.subheader("작업")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📄 PPT 생성하기", use_container_width=True):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{now}.pptx"

        ppt_buffer = BytesIO()

        # ppt_save 함수가 path 대신 file-like object를 받도록 수정
        ppt_save(song_list, ppt_buffer)

        ppt_buffer.seek(0)

        st.download_button(
            label="⬇️ PPT 다운로드",
            data=ppt_buffer,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )
