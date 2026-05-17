import streamlit as st
import os

# 設定 Streamlit 頁面為寬螢幕模式
st.set_page_config(layout="wide")

# 動態讀取同目錄下的 index.html 檔案
html_path = os.path.join(os.path.dirname(__file__), "index.html")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_code = f.read()
    
    # 【核心修正】：移除錯誤的 scroller=True，改用官方標準的 scrolling=True
    st.components.v1.html(html_code, height=950, scrolling=True)
else:
    st.error("找不到 index.html 檔案，請確認它與 app.py 在同一個資料夾內。")
