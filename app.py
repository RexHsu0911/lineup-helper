import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import datetime
import itertools

# =====================================================================
# 1. 狂盟專屬：天堂經典不朽黑紅暗金視覺風格 (CSS)
# =====================================================================
st.markdown("""
    <style>
    /* 全局狂盟戰場黑背景 */
    .main { background-color: #0d0d0d; color: #e0e0e0; font-family: 'Microsoft JhengHei', sans-serif; }
    /* 狂盟血深紅大標題 */
    h1 { color: #cc0000; text-align: center; font-weight: 900; text-shadow: 2px 2px 4px #000000; letter-spacing: 2px; }
    /* 鋼鐵不朽暗金邊框報告箱 */
    .report-box { background-color: #141414; border: 2px solid #8c7323; padding: 25px; border-radius: 8px; box-shadow: inset 0 0 10px #000; }
    /* 圖片小隊標題藍 */
    .img-title { color: #4a90e2; font-weight: bold; font-size: 16px; margin-top: 20px; display: block; }
    /* 黃字隊長 */
    .leader-y { color: #f39c12; font-weight: bold; padding-left: 15px; font-size: 15px; }
    /* 橘字隊長 */
    .leader-o { color: #d35400; font-weight: bold; padding-left: 15px; font-size: 15px; }
    /* 白字隊員 */
    .member-w { color: #dddddd; padding-left: 15px; margin: 4px 0; font-size: 15px; }
    /* 輸入標籤修正 */
    label { color: #8c7323 !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏰 狂盟血盟 - 行政秘書免費 AI 點名系統 V17</h1>", unsafe_allow_html=True)

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

st.markdown("<b style='color:#8c7323; font-size:16px;'>⚔️ 參戰資訊設定：</b>", unsafe_allow_html=True)

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

st.markdown("<hr style='border:0.5px solid #222;'>", unsafe_allow_html=True)

# 📸 圖片上傳區
uploaded_files = st.file_uploader(
    "📸 請上傳本次場次的所有遊戲截圖", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg'],
    key=f"uploader_{st.session_state.uploader_key}"
)

# 🔒 判斷目前是否有檔案正在處理/上傳中（防呆鎖機制核心）
is_uploading = False
if uploaded_files:
    # 展示縮圖
    st.markdown("<b style='color:#4a90e2;'>🖼️ 已上傳圖片縮圖預覽：</b>", unsafe_allow_html=True)
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, file in enumerate(uploaded_files):
        with cols[idx % 4]:
            file_bytes = file.read()
            file.seek(0)
            if len(file_bytes) == 0:  # 代表檔案還在傳輸讀取中
                is_uploading = True
            img_preview = Image.open(io.BytesIO(file_bytes))
            st.image(img_preview, caption=f"圖片 {idx+1}", use_container_width=True)

# =====================================================================
# 5. 鋼鐵律令提示詞（強逼單字隊長齊現身）
# =====================================================================
PROMPT_TEMPLATE = """
你現在是《天堂》遊戲的血盟行政秘書。這張圖片是隊伍名單截圖。
請你直奔「左下角隊伍 UI 區」，完全忽略右側聊天室（例如淡水柯景騰等雜訊）。

請嚴格、逐字對照以下【神盛核心白名單】：
什麼漾子、湊人數、和尚洗髮水、煙雨遙、小熊闖天下、波波鼠、筱駱駱、佛、紫楓秋夜、大都督、一小法一、蘇州賣鴨蛋、霸气小君、霸氣小君、天降神運、齊、粉色紅頭龜、飛翔的企鵝、168、紅心皇后、跑皮達人、柯基、粉色KITTY、夜駱駝。

【👑 紅色鋼鐵特級鐵律：隊長特別注意】
小隊的第一個名字（最上方的名字）絕對是隊長。
1. 本場指揮官「齊」如果出現在隊伍最上方，他是一個獨立的名字！他就是隊長！你絕對不准漏掉「齊」、不准跳過他，更不准用下面的隊員當隊長！
2. 「什麼漾子」、「筱駱駱」、「齊」這三個人只要出現在小隊中，他們必然是他們那張圖的隊長，必須強制排在第一行。

【🛡️ 鐵律：字體外觀注意】
請原封不動地輸出圖片中的字，如果是簡體的「霸气小君」，就必須輸出「霸气小君」，絕對不准擅自改成繁體！

【輸出格式】：
請精準依據以下格式輸出，名字後面括號寫(隊長)即可，不要回答任何額外的廢話：
[LEADER] 隊長名字
[MEMBER] 隊員1
[MEMBER] 隊員2
"""

VALID_NAMES = [
    "什麼漾子", "湊人數", "和尚洗髮水", "煙雨遙", "小熊闖天下", "波波鼠", 
    "筱駱駱", "佛", "紫楓秋夜", "大都督", "一小法一", "蘇州賣鴨蛋", "霸氣小君", "霸气小君", "天降神運", 
    "齊", "粉色紅頭龜", "飛翔的企鵝", "168", "紅心皇后", "跑皮達人", "柯基", "粉色KITTY", "夜駱駝"
]

# =====================================================================
# 6. 操作按鈕功能區 (加裝安全防呆鎖：is_uploading 成立時 disabled=True)
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if is_uploading:
        st.button("⏳ 圖片讀取中，請稍後...", disabled=True, use_container_width=True)
        execute_click = False
    else:
        execute_click = st.button("🔥 執行 100% 免費大模型精準名單認列", use_container_width=True)

with btn_col2:
    if is_uploading:
        st.button("🔄 清除按鈕鎖定中", disabled=True, use_container_width=True)
    else:
        if st.button("🔄 清除本場 / 恢復預設準備下一場", use_container_width=True):
            st.session_state.uploader_key += 1
            st.rerun()

# =====================================================================
# 7. 核心處理與報告輸出
# =====================================================================
if execute_click:
    if not api_key:
        st.error("⚠️ 老大，請先在左側邊欄填入您的 Google API 金鑰喔！")
    elif uploaded_files:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        date_str = selected_date.strftime("%Y%m%d")
        
        # 建立 Excel 三大欄位後台文字串 (欄位 A 序號獨立順延)
        raw_text_report = ""
        
        # 網頁端的圖形化精美顯示
        report_html = f"""
        <div class='report-box'>
            <span style='color: #cc0000; font-weight: bold; font-size: 18px;'>✨ 已為您讀取並認列此場次的隊員名單：</span><br>
            <div style='font-size: 15px; margin: 10px 0 20px 0; line-height:1.5;'>
                <b>場次資訊</b><br>
                • 日期: {date_str}<br>
                • 時間: {selected_time}<br>
                • 出團目標: {selected_target}<br>
                • 指揮官：{selected_commander}
            </div>
        """
        
        global_excel_idx = 1 # 用於 Excel 的全局序號
        
        for idx, file in enumerate(uploaded_files, start=1):
            file.seek(0)
            file_bytes = file.read()
            pil_image = Image.open(io.BytesIO(file_bytes))
            
            try:
                response = model.generate_content([PROMPT_TEMPLATE, pil_image])
                ai_output = response.text
                lines = ai_output.strip().split('\n')
                
                report_html += f"<span class='img-title'>📸 圖片 {idx} ({file.name}) 名單：</span><br>"
                
                # 🌟 老大交代：網頁端的每張小隊照片序號獨立從 1 開始計算！
                local_team_idx = 1 
                
                for line in lines:
                    clean_line = line.replace("[LEADER]", "").replace("[MEMBER]", "").replace("•", "").strip()
                    name_only = clean_line.split("(")[0].strip()
                    
                    if name_only in VALID_NAMES:
                        # Excel 底層儲存用的列公式（保持流水號往下走）
                        excel_row_base = f"{global_excel_idx}\t{date_str}\t{selected_time}\t{selected_target}\t{selected_commander}\t{name_only}"
                        
                        if name_only in ["什麼漾子", "筱駱駱", "齊"] or "(隊長)" in clean_line:
                            if name_only == "什麼漾子":
                                report_html += f"<div class='leader-y'>{local_team_idx}. {name_only} (隊長)</div>"
                            else:
                                report_html += f"<div class='leader-o'>{local_team_idx}. {name_only} (隊長)</div>"
                            raw_text_report += f"{excel_row_base}\t隊長\n"
                        else:
                            report_html += f"<div class='member-w'>{local_team_idx}. {name_only}</div>"
                            raw_text_report += f"{excel_row_base}\t\n"
                        
                        local_team_idx += 1
                        global_excel_idx += 1
                        
            except Exception as e:
                st.error(f"圖片 {idx} 辨識出錯：{e}")
                
        report_html += "</div>"
        
        # 1. 顯示網頁結果
        st.markdown(report_html, unsafe_allow_html=True)
        
        # 2. 顯示純文字框
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_area("📋 下方為專用 Excel 貼上格式數據（7大欄位）：", value=raw_text_report.strip(), height=250, key="copy_target")
        
        # 3. 鋼鐵狂盟紅一鍵複製大按鈕
        escaped_text = raw_text_report.strip().replace("`", "\\`").replace("'", "\\'")
        js_button_html = f"""
        <div style="text-align: center; width: 100%;">
            <button onclick="navigator.clipboard.writeText(`{escaped_text}`).then(() => alert('📋 報告老大：狂盟戰盟數據已成功複製！請前往 Excel 直接貼上。'));" 
            style="width: 100%; background-color: #cc0000; color: white; border: none; padding: 15px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.5);">
                📋 點我一鍵複製 Excel 7大欄位數據
            </button>
        </div>
        """
        st.components.v1.html(js_button_html, height=70)
