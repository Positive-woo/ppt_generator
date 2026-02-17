import streamlit as st
from pathlib import Path
from datetime import datetime
from io import BytesIO
from service.streamlit_function import plot_chroma_histogram, build_key_ranking_table
from service.ffmpeg_function import (
    extract_video_id,
    download_wav_to_tempfile,
    get_bpm_from_wav,
    get_key_from_wav,
)

st.set_page_config(
    page_title="BPM, Key 찾기",
    page_icon="🙏🏻",
    layout="wide",
)
st.title("🎵 YouTube Audio 분석기 // 웹페이지에서는 사용불가 ㅜㅜ")


import time


def log_time(msg, t0):
    now = time.time()
    print(f"[TIME] {msg}: {now - t0:.3f}s")
    return now


left, right = st.columns([1.2, 1])

with left:
    st.subheader("📺 YouTube 미리보기")
    url = st.text_input("YouTube URL")

    video_id = extract_video_id(url)
    if video_id:
        st.components.v1.iframe(
            src=f"https://www.youtube.com/embed/{video_id}",
            width="100%",
            height=400,
        )
    else:
        st.info("YouTube URL을 입력하면 미리보기가 표시됩니다.")


with right:
    st.subheader("🎼 음향 분석")

    if st.button("분석 시작", use_container_width=True):
        if not url:
            st.warning("YouTube URL을 입력하세요.")
        else:
            t = time.time()
            print("[TIME] start")

            with st.spinner("오디오 다운로드 및 분석 중..."):
                audio_buf = download_wav_to_tempfile(url)
                t = log_time("download_wav_to_memory", t)

                bpm = get_bpm_from_wav(audio_buf)
                t = log_time("get_bpm_from_buffer", t)

                result = get_key_from_wav(audio_buf)
                t = log_time("get_key_from_buffer", t)

            print(f"[TIME] totla : {time.time() - t:.3f}s")
            st.success("분석 완료")

            # ------------------
            # BPM & Primary Key (side by side)
            # ------------------
            col_bpm, col_key = st.columns(2)

            with col_bpm:
                st.subheader("⏱ BPM")
                st.markdown(f"## **{int(round(bpm))}**", unsafe_allow_html=True)

            with col_key:
                primary = result["primary_key"]
                st.subheader("🎵 예상 키")
                st.markdown(
                    f"## **{primary['key']} {primary['mode']}**  \n"
                    f"<span style='color:gray'>(correlation = {primary['score']:.3f})</span>",
                    unsafe_allow_html=True,
                )

            # ------------------
            # Chroma Histogram
            # ------------------
            st.subheader("🎹 음별 에너지 분포")
            fig = plot_chroma_histogram(result["chroma_vector"])
            st.pyplot(fig)

            # ------------------
            # Key Ranking Table
            # ------------------
            st.subheader("📊 키 후보 랭킹")
            df_rank = build_key_ranking_table(result["ranked_candidates"], top_n=10)
            st.dataframe(df_rank, use_container_width=True)
