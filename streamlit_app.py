# -*- coding: utf-8 -*-
"""통영 아웃리치 식사팀 가이드 — Streamlit 래퍼.
   디자인(정적 HTML)을 그대로 스트림릿 안에 띄웁니다."""
import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="통영 아웃리치 식사팀", page_icon="🍚",
                   layout="centered", initial_sidebar_state="collapsed")

# 스트림릿 기본 UI(헤더/푸터/여백) 숨겨서 앱처럼 보이게
st.markdown("""
<style>
  header[data-testid="stHeader"]{display:none}
  #MainMenu, footer{visibility:hidden}
  .block-container{padding:0 !important;max-width:100% !important}
  [data-testid="stAppViewContainer"]{background:#e9e6e3}
  iframe{display:block;margin:0 auto}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent

def b64(path, mime):
    data = (ROOT / path).read_bytes()
    return f"data:{mime};base64," + base64.b64encode(data).decode()

html = (ROOT / "app_embedded.html").read_text(encoding="utf-8")
html = html.replace("__POSTER__", b64("assets/poster.png", "image/png"))
html = html.replace("__TEAM__",   b64("assets/team.jpg",   "image/jpeg"))

# 높이는 기기에 맞춰 조절 가능 (숫자만 바꾸면 됩니다)
components.html(html, height=880, scrolling=True)
