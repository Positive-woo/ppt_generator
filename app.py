from service.streamlit_function import load_css
import streamlit as st
from PIL import Image, ImageOps
from dotenv import load_dotenv

load_dotenv()

img = Image.open("source/dashboard.jpeg")
img = ImageOps.exif_transpose(img)

load_css("css/wide.css")

st.set_page_config(
    page_title="동부교회 청년부 자막 생성기",
    page_icon="🙏🏻",
    layout="wide",
)


st.title("동부교회 청년부 자막 생성기 🙏🏻")
st.write("")
st.image(img, width=600)

st.divider()
st.caption("build : 20251228")

# chmod +x run.command
# kill $(lsof -t -i :8502)
