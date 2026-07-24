import streamlit as st


def init_auto_maker_session() -> None:
    defaults = {
        "auto_maker_search_query": "",
        "auto_maker_trigger_search": False,
        "auto_maker_prev_selected_song_key": None,
        "auto_maker_search_results": [],
        "auto_maker_part_count": 3,
        "auto_maker_reset_counter": 0,
        "auto_maker_song_form": "",
        "auto_maker_autofill_result": None,
        "auto_maker_autofill_apply": None,
        "auto_maker_sunday_preview_text": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    pending_autofill = st.session_state.pop("auto_maker_autofill_apply", None)
    if not isinstance(pending_autofill, dict):
        return

    song_form = str(pending_autofill.get("song_form", "")).strip()
    song_name = str(pending_autofill.get("song_name", "")).strip()
    part_items = [
        (k, v)
        for k, v in pending_autofill.items()
        if k not in ["song_name", "song_form", "error", "raw"]
    ]

    st.session_state.auto_maker_song_form = song_form
    if song_name:
        st.session_state.auto_maker_song_title = song_name

    st.session_state.auto_maker_part_count = max(1, len(part_items))
    new_reset_counter = st.session_state.get("auto_maker_reset_counter", 0) + 1
    st.session_state.auto_maker_reset_counter = new_reset_counter

    for i, (part_name, part_lyrics) in enumerate(part_items):
        st.session_state[f"auto_maker_part_name_{i}_{new_reset_counter}"] = str(
            part_name
        )
        st.session_state[f"auto_maker_part_lyrics_{i}_{new_reset_counter}"] = str(
            part_lyrics
        )

    st.session_state.auto_maker_sunday_preview_text = ""
