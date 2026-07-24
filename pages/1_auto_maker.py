from service.auto_maker_component import (
    upload_button,
    render_song_boxes,
    load_song_grid_css,
    render_lyrics_tool_title,
    render_lyrics_search_panel,
    render_lyrics_editor_header,
    render_lyrics_editor_text_area,
    render_song_form_editor_panel,
    render_autofill_result_panel,
)
from service.openai_function import ask_openai_json, request_openai_autofill
from service.streamlit_function import (
    crawl_lyrics,
    crawl_track_lyrics,
    collect_auto_maker_parts,
    build_sunday_text,
    handle_generate_action,
)
from service.auto_maker_session import init_auto_maker_session
import streamlit as st
import json
import base64


load_song_grid_css()

st.set_page_config(page_title="악보 자동 분석", layout="wide")

st.title("📂 악보 자동 곡 분리기")

uploaded_files = upload_button()  # list

if uploaded_files:
    st.write("이미지 파싱")
    st.write(f"총 이미지 수 : {len(uploaded_files)}")
    st.write(uploaded_files)

# test = '{"song_1":[{"song_name":"밝은 빛이 가득해","song_form":"(8)AAB(8)AABBB(+우린기뻐노래해x2)","A":"밝은 빛이 가득해","B":"받아주시네 기뻐해 찬양해"}],"song_2":[{"song_name":"내 마음을 가득 채운","song_form":"(8)A1A1BA2BB(8)CCBBB(8)","A1":"내 마음을 가득 채운 주 향한 찬양과 사랑","A2":"수많은 찬양들로 그 맘 표현할","B":"주 사랑해요 온 맘 다하여","C":"주님 사랑 다시 고백하는 찬양"}],"song_3":[{"song_name":"주의 자녀로 산다는 것은 / 부르신 곳에서","song_form":"A1A2B(16)A1A2BB(1)A3A4BBB->B0B0C0C0","A1":"주의 자녀로 산다는 것은","A2":"의 자녀로 산다는 것은","B":"데 힘쓸 때도 폭풍 가운데 무너질 때도","A3":"의 자녀로 산다는 것은","A4":"의 자녀로 산다는 것은","B0":"걸어갈 때 길이 되고 살아갈 때 삶이 되는","C0":"나는 예배하네 어떤 상황에도"}]}'
# if st.button("test"):
#     st.session_state.auto_maker_result = json.loads(test)

if st.button("전송"):
    result = ask_openai_json(uploaded_files)
    st.session_state.auto_maker_result = result

init_auto_maker_session()

if "auto_maker_result" in st.session_state:
    st.write(st.session_state.auto_maker_result)
    selected_song = render_song_boxes(st.session_state.auto_maker_result)
    if selected_song:
        st.session_state.auto_maker_selected_song = selected_song
        selected_key = st.session_state.get("selected_song_key")
        prev_selected_key = st.session_state.get("auto_maker_prev_selected_song_key")
        song_name = selected_song.get("song_name", "").strip()

        if selected_key != prev_selected_key and song_name:
            st.session_state.auto_maker_prev_selected_song_key = selected_key
            st.session_state.auto_maker_search_query = song_name
            st.session_state.auto_maker_trigger_search = True
            st.rerun()

st.divider()
render_lyrics_tool_title()

col_left, col_center, col_right = st.columns([1.5, 1.3, 1.5])

with col_left:
    render_lyrics_search_panel(crawl_lyrics, crawl_track_lyrics)

with col_center:
    generate_clicked = render_lyrics_editor_header()
    handle_generate_action(generate_clicked, request_openai_autofill)
    render_lyrics_editor_text_area()

with col_right:
    render_song_form_editor_panel()

if st.session_state.get("auto_maker_autofill_result") is not None:
    current_song_form = st.session_state.get("auto_maker_song_form", "")
    current_parts = collect_auto_maker_parts()
    current_title = st.session_state.get("auto_maker_song_title", "")

    if not st.session_state.auto_maker_sunday_preview_text:
        st.session_state.auto_maker_sunday_preview_text = build_sunday_text(
            song_form=current_song_form,
            parts=current_parts,
            title=current_title,
        )

    regenerate_clicked = render_autofill_result_panel(
        autofill_result=st.session_state.auto_maker_autofill_result,
        sunday_preview_text=st.session_state.auto_maker_sunday_preview_text,
    )

    if regenerate_clicked:
        current_song_form = st.session_state.get("auto_maker_song_form", "")
        current_parts = collect_auto_maker_parts()
        current_title = st.session_state.get("auto_maker_song_title", "")
        st.session_state.auto_maker_sunday_preview_text = build_sunday_text(
            song_form=current_song_form,
            parts=current_parts,
            title=current_title,
        )
        st.toast("주일예배용 텍스트를 다시 생성했습니다.", icon="✅")
