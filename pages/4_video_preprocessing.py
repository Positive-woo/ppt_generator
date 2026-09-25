import streamlit as st
import tempfile
import os
import base64
from pathlib import Path
from service.video_function import get_video_info, extract_frame_bytes, compute_crop, export_video

st.set_page_config(page_title="비디오 전처리", page_icon="🎬", layout="wide")
st.title("🎬 비디오 전처리")

RATIO_PRESETS = {
    "원본": None,
    "16:9": "16:9",
    "21:9": "21:9",
    "9:16": "9:16",
    "1:1": "1:1",
    "4:3": "4:3",
    "✏️ 직접 입력": "custom",
}


@st.cache_data
def cached_frame(path: str, time: float) -> bytes:
    return extract_frame_bytes(path, time)


def render_preview(b64: str, vid_w: int, vid_h: int, cw: int, ch: int, cx: int, cy: int):
    has_crop = not (cx == 0 and cy == 0 and cw == vid_w and ch == vid_h)

    if not has_crop:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{b64}" style="width:100%;border-radius:8px;display:block;" />',
            unsafe_allow_html=True,
        )
        return

    top_pct    = cy / vid_h * 100
    bot_pct    = (vid_h - cy - ch) / vid_h * 100
    left_pct   = cx / vid_w * 100
    right_pct  = (vid_w - cx - cw) / vid_w * 100
    mid_h_pct  = ch / vid_h * 100
    mid_w_pct  = cw / vid_w * 100
    dark = "rgba(0,0,0,0.55)"

    st.markdown(
        f"""
        <div style="position:relative;display:inline-block;width:100%;border-radius:8px;overflow:hidden;">
            <img src="data:image/jpeg;base64,{b64}" style="width:100%;display:block;" />
            <div style="position:absolute;top:0;left:0;right:0;height:{top_pct:.2f}%;background:{dark};"></div>
            <div style="position:absolute;bottom:0;left:0;right:0;height:{bot_pct:.2f}%;background:{dark};"></div>
            <div style="position:absolute;top:{top_pct:.2f}%;left:0;width:{left_pct:.2f}%;height:{mid_h_pct:.2f}%;background:{dark};"></div>
            <div style="position:absolute;top:{top_pct:.2f}%;right:0;width:{right_pct:.2f}%;height:{mid_h_pct:.2f}%;background:{dark};"></div>
            <div style="position:absolute;top:{top_pct:.2f}%;left:{left_pct:.2f}%;width:{mid_w_pct:.2f}%;height:{mid_h_pct:.2f}%;
                border:2px solid rgba(255,255,255,0.9);box-sizing:border-box;pointer-events:none;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Upload ─────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("영상 파일 선택", type=["mp4", "mov", "avi", "mkv"])

if not uploaded:
    st.info("영상 파일을 업로드하면 편집 화면이 표시됩니다.")
    st.stop()

# 파일이 바뀔 때만 tmp 저장
file_key = f"{uploaded.name}_{uploaded.size}"
if st.session_state.get("video_file_key") != file_key:
    if old := st.session_state.get("video_tmp_path"):
        try:
            os.unlink(old)
        except Exception:
            pass
    suffix = Path(uploaded.name).suffix or ".mp4"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp.write(uploaded.read())
    tmp.close()
    st.session_state.video_tmp_path = tmp.name
    st.session_state.video_file_key = file_key
    st.session_state.video_info = get_video_info(tmp.name)
    st.session_state.pop("export_result", None)

info = st.session_state.video_info
video_path = st.session_state.video_tmp_path

if not info:
    st.error("영상 정보를 읽을 수 없습니다.")
    st.stop()

duration = info["duration"]
vid_w = info["width"]
vid_h = info["height"]

# ── Preview + Controls ─────────────────────────────────────────────────────
col_preview, col_controls = st.columns([3, 1])

with col_controls:
    st.markdown("#### ⚡ 속도")
    speed = st.slider(
        "speed", 0.5, 2.0, 1.0, 0.05,
        key="speed", format="%.2fx",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("#### ✂️ 크롭 비율")
    selected_label = st.radio(
        "ratio", list(RATIO_PRESETS.keys()),
        key="ratio_label",
        label_visibility="collapsed",
    )
    ratio_str = RATIO_PRESETS[selected_label]

    if ratio_str == "custom":
        c1, c2 = st.columns(2)
        cw_in = c1.number_input("가로", 1, 100, 16, key="custom_w")
        ch_in = c2.number_input("세로", 1, 100, 9, key="custom_h")
        ratio_str = f"{cw_in}:{ch_in}"

    cw, ch, cx_center, cy_center = compute_crop(vid_w, vid_h, ratio_str)

    # 위치 조절 슬라이더 (크롭이 활성화된 경우만)
    if ratio_str:
        ratio_key = ratio_str.replace(":", "x")
        st.markdown("---")
        st.markdown("#### 📍 위치 조정")

        max_cx = vid_w - cw
        max_cy = vid_h - ch

        cx = st.slider(
            "↔ 좌우", 0, max(max_cx, 1), min(cx_center, max_cx),
            key=f"cx_{ratio_key}",
            disabled=(max_cx == 0),
        ) if max_cx > 0 else 0

        cy = st.slider(
            "↕ 상하", 0, max(max_cy, 1), min(cy_center, max_cy),
            key=f"cy_{ratio_key}",
            disabled=(max_cy == 0),
        ) if max_cy > 0 else 0
    else:
        cx, cy = 0, 0

    st.markdown("---")
    st.caption(f"원본  {vid_w} × {vid_h}")
    if ratio_str:
        st.caption(f"크롭  {cw} × {ch}  @ ({cx}, {cy})")
    st.caption(f"속도  {speed:.2f}x")

with col_preview:
    trim_state = st.session_state.get("trim_range", (0.0, duration))
    preview_time = max(trim_state[0] if isinstance(trim_state, (list, tuple)) else 0.0, 0.1)

    # 미리보기 모드 전환 버튼
    preview_mode = st.session_state.get("preview_mode", "frame")
    btn_col1, btn_col2 = st.columns(2)
    if btn_col1.button("🖼 프레임 보기", use_container_width=True, type="secondary" if preview_mode == "video" else "primary"):
        st.session_state.preview_mode = "frame"
        st.rerun()
    if btn_col2.button("▶ 영상 미리보기 (5초)", use_container_width=True, type="primary" if preview_mode == "video" else "secondary"):
        crop = (cw, ch, cx, cy) if (cx or cy or cw != vid_w or ch != vid_h) else None
        trim_end_preview = trim_state[1] if isinstance(trim_state, (list, tuple)) else duration
        with st.spinner("미리보기 생성 중..."):
            try:
                preview_end = min(preview_time + 5.0, trim_end_preview)
                clip = export_video(video_path, preview_time, preview_end, crop, speed, web_preview=True)
                st.session_state.preview_clip = clip
                st.session_state.preview_mode = "video"
            except Exception as e:
                st.error(f"미리보기 실패: {e}")
        st.rerun()

    if st.session_state.get("preview_mode") == "video" and st.session_state.get("preview_clip"):
        st.video(st.session_state.preview_clip)
    else:
        frame = cached_frame(video_path, preview_time)
        if frame:
            b64 = base64.b64encode(frame).decode()
            render_preview(b64, vid_w, vid_h, cw, ch, cx, cy)

# ── Trim ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### ✂️ 트림 (앞뒤 자르기)")
trim_range = st.slider(
    "trim", 0.0, max(duration, 0.1), (0.0, duration), 0.1,
    key="trim_range", format="%.1f초",
    label_visibility="collapsed",
)
trim_start, trim_end = trim_range
st.caption(f"{trim_start:.1f}초 ~ {trim_end:.1f}초  (구간 {trim_end - trim_start:.1f}초)")

# ── Export ─────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("🎬 영상 내보내기", use_container_width=True, type="primary"):
    crop = (cw, ch, cx, cy) if (cx or cy or cw != vid_w or ch != vid_h) else None

    with st.spinner("ffmpeg 처리 중..."):
        try:
            result_bytes = export_video(video_path, trim_start, trim_end, crop, speed)
            st.session_state.export_result = result_bytes
            st.success("처리 완료!")
        except Exception as e:
            st.error(f"처리 실패: {e}")

if result := st.session_state.get("export_result"):
    st.download_button(
        "💾 다운로드",
        result,
        file_name="output.mp4",
        mime="video/mp4",
        use_container_width=True,
    )
