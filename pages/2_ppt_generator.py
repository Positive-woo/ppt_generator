from datetime import datetime
from service.streamlit_function import ppt_save
from io import BytesIO
from pathlib import Path
import streamlit as st
import ast

SUMMER_TEMPLATE_PATH = Path("source/ppt_template/template.pptx")


def create_ppt_download(song_list, file_name, template=None, key="ppt_download"):
    if not song_list:
        st.warning("먼저 PPT로 만들 곡 정보를 입력해주세요.")
        return

    ppt_buffer = BytesIO()
    ppt_save(song_list, ppt_buffer, template=template)
    ppt_buffer.seek(0)

    st.download_button(
        label="⬇️ PPT 다운로드",
        data=ppt_buffer,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        use_container_width=True,
        key=key,
    )


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
song_list = None

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
    else:
        song_list = st.session_state.get("song_list")

# ----------------------
# Right: Action Button
# ----------------------
with col_right:
    st.subheader("작업")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📄 PPT 생성하기", use_container_width=True):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{now}.pptx"

        try:
            create_ppt_download(song_list, file_name, key="default_ppt_download")
        except Exception as e:
            st.error(f"PPT 생성 실패: {e}")

    if st.button("26_하계_PPT_생성하기", use_container_width=True):
        if not SUMMER_TEMPLATE_PATH.exists():
            st.warning(f"템플릿 파일을 찾을 수 없습니다: {SUMMER_TEMPLATE_PATH}")
        else:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"26_하계_{now}.pptx"

            try:
                create_ppt_download(
                    song_list,
                    file_name,
                    template=SUMMER_TEMPLATE_PATH,
                    key="summer_2026_ppt_download",
                )
            except Exception as e:
                st.error(f"26_하계 PPT 생성 실패: {e}")
