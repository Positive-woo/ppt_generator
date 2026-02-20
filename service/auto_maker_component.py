import streamlit as st
import base64
from pdf2image import convert_from_bytes
from PIL import Image
import io
import html


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


# def render_song_boxes(result: dict):
#     songs = list(result.keys())
#     max_per_row = 5

#     for i in range(0, len(songs), max_per_row):

#         cols = st.columns(max_per_row)

#         for col_index in range(max_per_row):

#             song_index = i + col_index

#             if song_index >= len(songs):
#                 break

#             song_key = songs[song_index]
#             song_data = result[song_key][0]

#             with cols[col_index]:
#                 with st.container(border=True):

#                     st.subheader(song_data.get("song_name", "Unknown"))

#                     st.caption(song_data.get("song_form", ""))

#                     for k, v in song_data.items():
#                         if k not in ["song_name", "song_form"]:
#                             st.write(f"**{k}** : {v}")


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
