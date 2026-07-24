import streamlit as st
import base64
from pdf2image import convert_from_bytes
from PIL import Image
import io
import html
from typing import Callable


def upload_button():
    uploaded_files = st.file_uploader(
        "PDF 또는 이미지 업로드",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    if not uploaded_files:
        return []

    images_base64 = []

    for file in uploaded_files:

        # 1️⃣ PDF인 경우
        if file.type == "application/pdf":
            pdf_bytes = file.read()
            pages = convert_from_bytes(pdf_bytes)

            for page in pages:
                buffer = io.BytesIO()
                page.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                images_base64.append(img_base64)

        # 2️⃣ 이미지인 경우
        else:
            image = Image.open(file)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            images_base64.append(img_base64)

    return images_base64


def load_song_grid_css():
    st.markdown(
        """
    <style>
    .song-grid {
        display: grid;
        grid-template-columns: repeat(var(--song-cols, 5), minmax(0, 1fr));
        gap: 16px;
        width: 100%;
    }

    .song-box {
        height: 260px;              /* 고정 높이 */
        overflow-y: auto;           /* 내용 넘치면 스크롤 */
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 12px;
        background-color: #fafafa;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    .song-box-selected {
        border: 2px solid #1f77b4;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.12);
    }

    .song-title {
        font-weight: 600;
        font-size: 16px;
    }

    .song-form {
        font-size: 13px;
        color: gray;
        margin-bottom: 8px;
    }

    .section-row {
        display: flex;
        align-items: baseline;
        gap: 6px;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
    }

    .section-label {
        font-weight: 700;
        flex-shrink: 0;
    }

    .section-content {
        flex: 1;
        min-width: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_song_boxes(result: dict):
    if not result:
        st.info("표시할 곡이 없습니다.")
        return None

    songs = list(result.items())
    song_cols = max(1, min(5, len(songs)))

    selected_key = st.session_state.get("selected_song_key")
    if selected_key not in result:
        selected_key = songs[0][0]
        st.session_state["selected_song_key"] = selected_key

    for row_start in range(0, len(songs), song_cols):
        row_items = songs[row_start : row_start + song_cols]
        cols = st.columns(song_cols)

        for col_index, col in enumerate(cols):
            with col:
                if col_index >= len(row_items):
                    st.empty()
                    continue

                song_key, song_list = row_items[col_index]
                song = song_list[0] if song_list else {}
                is_selected = song_key == selected_key
                card_class = "song-box song-box-selected" if is_selected else "song-box"

                card_html = f'<div class="{card_class}">'
                card_html += f'<div class="song-title">{html.escape(str(song.get("song_name", "")))}</div>'
                card_html += f'<div class="song-form">{html.escape(str(song.get("song_form", "")))}</div>'

                for k, v in song.items():
                    if k not in ["song_name", "song_form"]:
                        card_html += (
                            '<div class="section-row">'
                            f'<span class="section-label">{html.escape(str(k))} :</span>'
                            f'<span class="section-content">{html.escape(str(v))}</span>'
                            "</div>"
                        )

                card_html += "</div>"
                st.markdown(card_html, unsafe_allow_html=True)

                button_label = "선택됨" if is_selected else "선택"
                button_type = "primary" if is_selected else "secondary"
                if st.button(
                    button_label,
                    key=f"select_song_box_{song_key}",
                    type=button_type,
                    use_container_width=True,
                ):
                    st.session_state["selected_song_key"] = song_key
                    st.session_state["selected_song_data"] = song
                    st.rerun()

    selected_key = st.session_state.get("selected_song_key")
    if selected_key in result and result[selected_key]:
        st.session_state["selected_song_data"] = result[selected_key][0]
        return result[selected_key][0]

    return None


def render_lyrics_tool_title() -> None:
    st.subheader("🎶 자동 생성기")


def render_lyrics_search_panel(
    crawl_lyrics: Callable[[str], list],
    crawl_track_lyrics: Callable[[str], str],
) -> None:
    current_track_id = st.session_state.get("auto_maker_track_id")
    prev_track_id = st.session_state.get("auto_maker_prev_track_id")
    if current_track_id and current_track_id != prev_track_id:
        try:
            st.session_state.auto_maker_lyrics_text = crawl_track_lyrics(
                current_track_id
            )
            st.session_state.auto_maker_prev_track_id = current_track_id
        except Exception as e:
            st.toast(f"가사 불러오기 실패: {e}", icon="❌")

    st.subheader("곡 목록")

    with st.form(key="auto_maker_search_form"):
        query = st.text_input(
            label="",
            placeholder="곡명 또는 가수 검색",
            key="auto_maker_search_query",
        )
        submitted = st.form_submit_button("🔎 검색", use_container_width=True)
    auto_search = st.session_state.pop("auto_maker_trigger_search", False)

    if submitted or auto_search:
        if not query.strip():
            st.toast("검색어를 입력하세요.", icon="⚠️")
        else:
            try:
                results = crawl_lyrics(query)
                st.session_state.auto_maker_search_results = results
                st.toast("검색 완료", icon="✅")
            except Exception as e:
                st.toast(f"검색 실패: {e}", icon="❌")

    st.divider()
    results = st.session_state.get("auto_maker_search_results", [])
    if not results:
        st.info("검색 결과가 여기에 표시됩니다. (상위 8개만 표시)")
        return

    for idx, r in enumerate(results):
        title = html.escape(str(r.get("title", "")))
        artist = html.escape(str(r.get("artist", "")))
        st.markdown(
            f"""
            <div class="song-card-wrapper">
                <div class="song-card">
                    <div class="song-title">{title}</div>
                    <div class="song-artist">{artist}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "select",
            key=f"auto_maker_search_select_{idx}",
            use_container_width=True,
        ):
            st.session_state.auto_maker_song_title = r.get("title", "")
            st.session_state.auto_maker_song_artist = r.get("artist", "")
            track_id = r.get("track_id", "")
            st.session_state.auto_maker_track_id = track_id
            if track_id:
                try:
                    st.session_state.auto_maker_lyrics_text = crawl_track_lyrics(
                        track_id
                    )
                    st.session_state.auto_maker_prev_track_id = track_id
                except Exception as e:
                    st.toast(f"가사 불러오기 실패: {e}", icon="❌")
            st.rerun()


def render_lyrics_editor_header() -> bool:
    header_col, button_col = st.columns([3, 2], gap="small")
    with header_col:
        st.subheader("가사")
    with button_col:
        generate_clicked = st.button(
            "자동생성",
            key="auto_maker_generate_btn",
            use_container_width=True,
        )
    return generate_clicked


def render_lyrics_editor_text_area() -> None:
    st.text_area(
        label="",
        height=700,
        placeholder="검색 후 선택하면 가사가 표시됩니다.",
        key="auto_maker_lyrics_text",
    )


def render_song_form_editor_panel(
    part_count_key: str = "auto_maker_part_count",
    reset_counter_key: str = "auto_maker_reset_counter",
) -> str:
    st.subheader("송폼")
    song_form = st.text_input(
        label="송폼",
        placeholder="예: A1BCBB(4)A2BBC",
        key="auto_maker_song_form",
    )

    st.divider()

    part_count = st.session_state.get(part_count_key, 3)
    reset_counter = st.session_state.get(reset_counter_key, 0)

    for i in range(part_count):
        header_col, _ = st.columns([1, 3])
        with header_col:
            st.text_input(
                label="",
                placeholder="part",
                key=f"auto_maker_part_name_{i}_{reset_counter}",
            )
        st.text_area(
            label=f"가사 {i + 1}",
            height=120,
            placeholder="가사를 넣어주세요",
            key=f"auto_maker_part_lyrics_{i}_{reset_counter}",
        )
        st.divider()

    if st.button("➕ 파트 추가", use_container_width=True, key="auto_maker_add_part"):
        st.session_state[part_count_key] = part_count + 1

    return song_form


def render_autofill_result_panel(
    autofill_result: dict | None,
    sunday_preview_text: str,
) -> bool:
    if autofill_result is None:
        return False

    st.subheader("자동생성 결과")
    regenerate_clicked = st.button(
        "재 생성",
        key="auto_maker_regenerate_btn",
        use_container_width=True,
    )

    left_result_col, right_result_col = st.columns([1, 1])

    with left_result_col:
        st.json(autofill_result)

    with right_result_col:
        st.text_area(
            label="",
            value=sunday_preview_text,
            height=1000,
        )

    return regenerate_clicked
