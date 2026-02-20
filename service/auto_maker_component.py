import streamlit as st
import base64
from pdf2image import convert_from_bytes
from PIL import Image
import io


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
    song_cols = max(1, min(5, len(result)))
    html = f'<div class="song-grid" style="--song-cols:{song_cols};">'

    for song_key in result:
        song = result[song_key][0]

        html += '<div class="song-box">'
        html += f'<div class="song-title">{song.get("song_name","")}</div>'
        html += f'<div class="song-form">{song.get("song_form","")}</div>'

        for k, v in song.items():
            if k not in ["song_name", "song_form"]:
                html += (
                    '<div class="section-row">'
                    f'<span class="section-label">{k} :</span>'
                    f'<span class="section-content">{v}</span>'
                    "</div>"
                )

        html += "</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)
