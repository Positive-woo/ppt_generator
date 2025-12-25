from service.streamlit_function import load_css
import streamlit as st

load_css("css/wide.css")

st.set_page_config(
    page_title="동부교회 청년부 자막 생성기",
    page_icon="🙏🏻",
    layout="wide",
)


st.title("동부교회 청년부 자막 생성기 🙏🏻")
st.write("대시보드 화면")

st.divider()
st.caption("build : 20251225")

# chmod +x run.command
# kill $(lsof -t -i :8502)
