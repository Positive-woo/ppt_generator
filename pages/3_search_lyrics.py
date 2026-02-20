import streamlit as st
from service.streamlit_function import (
    reset_session,
    export_retreat,
    export_holiday,
    crawl_lyrics,
    sync_lyrics_with_track,
    listup_lyrics_result,
)
from service.streamlit_function import load_css
from service.search_lyrics_component import (
    render_title_bar,
    render_search_column,
    render_lyrics_column,
    render_song_form_column,
    render_export_actions,
    render_extracted_result,
)

st.set_page_config(
    page_title="가사 검색기",
    page_icon="🙏🏻",
    layout="wide",
)

load_css("css/wide.css")

if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0
if "part_count" not in st.session_state:
    st.session_state.part_count = 3
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "selected_song" not in st.session_state:
    st.session_state.selected_song = None
if "lyrics_text" not in st.session_state:
    st.session_state.lyrics_text = ""

sync_lyrics_with_track()
render_title_bar(reset_session)

col_left, col_center, col_right = st.columns([1.5, 1.3, 1.5])


with col_left:
    render_search_column(crawl_lyrics, listup_lyrics_result)


with col_center:
    render_lyrics_column()


with col_right:
    song_form = render_song_form_column()

render_export_actions(song_form, export_holiday, export_retreat)
render_extracted_result()
