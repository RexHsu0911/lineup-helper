import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import datetime
import itertools

# =====================================================================
# 1. 網頁頂級金黑神殿視覺風格 (CSS)
# =====================================================================
st.markdown("""
    <style>
    .main { background-color: #121212; color: #ffffff; }
    h1 { color: #f1c40f; text-align: center; font-family: 'Microsoft JhengHei'; }
    .report-box { background-color: #1a1a1a; border: 2px solid #d4af37; padding: 25px; border-radius: 12px; }
    .img-title { color: #3498db; font-weight: bold; font-size: 16px; margin-top: 20px; display: block; }
    .leader-y { color: #f1c40f; font-weight: bold; padding-left: 15px; }
    .leader-o { color: #e67e22; font-weight: bold; padding-left: 15px; }
    .member-w { color: #ffffff; padding-left: 15px; margin: 3px 0; }
    </style>
""", unsafe_allow_html=True)

st.title("🏰 天堂血盟 - 行政秘書免費 AI 網頁系統 V15")

# =====================================================================
# 2. 自動生成所有出團目標的排列組合
# =====================================================================
base_targets = ["四色", "飛龍", "伊佛", "蟻媽媽", "克特", "掃街", "打架"]
all_combinations = []
for r in range(1, len(base_targets) + 1):
    for combo in itertools.combinations(base_targets, r):
        all_combinations.append("+".join(combo))

if "飛龍+四色+伊佛" in all_combinations:
    all_combinations.remove("飛龍+四色+伊佛")
all_combinations.insert(0, "飛龍+四色+伊佛")

COMMANDER_LIST = ["齊", "什麼漾子", "筱駱駱", "夜駱駝", "大都督", "副盟主1", "副盟主2"]

# =====================================================================
# 3. 初始化記憶庫
# =====================================================================
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# =====================================================================
# 4. 前端選單輸入區
# =====================================================================
api_key = st.sidebar.text_input("🔑 請輸入 Google Gemini API Key:", type="password")

st.markdown("<b style='color:#f1c40f; font-size:16px;'>⚔️ 參戰資訊設定：</b>", unsafe_allow_html=True)

col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input("📅 選擇日期:", datetime.date(2026, 5, 17))
with col_time:
    time_options = [f"{str(h).zfill(2)}00" for h in range(24)]
    selected_time = st.selectbox("⏰ 選擇時間 (每小時為單位):", options=time_options, index=8)

col_target, col_cmd = st.columns(2)
with col_target:
    selected_target = st.selectbox("🎯 出團目標 (已包含所有排列組合):", options=all_combinations)
with col_cmd:
    selected_commander = st.selectbox("👑 本場指揮官:", options=COMMANDER_LIST, index=0)

st.markdown("<hr style='border:0.5px solid #333;'>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "📸 請上傳本次場次的所有遊戲截圖", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg'],
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    st.markdown("<b style='color:#3498db;'>🖼️ 已上傳圖片縮圖預覽：</b>", unsafe_allow_html=True)
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, file in enumerate(uploaded_files):
        with cols[idx % 4]:
            file_bytes = file.read()
            file.seek(0)
            img
