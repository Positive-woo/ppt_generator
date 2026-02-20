from typing import Callable

import streamlit as st


def render_title_bar(on_reset: Callable[[], None]) -> None:
    title_col, reset_col = st.columns([5, 1])

    with title_col:
        st.title("🎶 가사 검색기")

    with reset_col:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 리셋"):
            on_reset()


def render_search_column(
    crawl_lyrics: Callable[[str], list],
    listup_lyrics_result: Callable[[list], None],
) -> None:
    st.subheader("곡 목록")

    with st.form(key="search_form"):
        query = st.text_input(
            label="",
            placeholder="곡명 또는 가수 검색",
            key="search_query",
        )
        submitted = st.form_submit_button("🔎 검색", use_container_width=True)

    if submitted:
        if not query.strip():
            st.toast("검색어를 입력하세요.", icon="⚠️")
        else:
            try:
                results = crawl_lyrics(query)
                st.session_state.search_results = results
                st.toast("검색 완료", icon="✅")
            except Exception as e:
                st.toast(f"검색 실패: {e}", icon="❌")

    st.divider()
    results = st.session_state.get("search_results", [])
    listup_lyrics_result(results)


def render_lyrics_column() -> None:
    st.subheader("가사")
    st.text_area(
        label="",
        height=1200,
        placeholder="검색 후 선택하면 가사가 표시됩니다.",
        key="lyrics_text",
    )


def render_song_form_column() -> str:
    st.subheader("송폼")
    song_form = st.text_input(
        label="송폼",
        placeholder="예: A1BCBB(4)A2BBC",
    )

    st.divider()

    for i in range(st.session_state.part_count):
        header_col, _ = st.columns([1, 3])
        with header_col:
            st.text_input(
                label="",
                placeholder="part",
                key=f"part_name_{i}_{st.session_state.reset_counter}",
            )
        st.text_area(
            label=f"가사 {i + 1}",
            height=120,
            placeholder="가사를 넣어주세요",
            key=f"part_lyrics_{i}_{st.session_state.reset_counter}",
        )
        st.divider()

    if st.button("➕ 파트 추가", use_container_width=True):
        st.session_state.part_count += 1

    return song_form


def render_export_actions(
    song_form: str,
    export_holiday: Callable[[str], str],
    export_retreat: Callable[[str], None],
) -> None:
    if st.button("🙏🏻 주일예배 추출하기", use_container_width=True):
        export_holiday(song_form)
        st.session_state.export_type = "sunday"
        st.toast("복사되었습니다 ✅", icon="📋")

    if st.button("📤 수련회용 추출하기", use_container_width=True):
        export_retreat(song_form)
        st.session_state.export_type = "retreat"
        st.toast("복사되었습니다 ✅", icon="📋")


def render_extracted_result() -> None:
    if "extracted_text" in st.session_state:
        st.subheader("📋 추출 결과")
        st.text_area(
            label="",
            value=st.session_state.extracted_text,
            height=320,
        )
