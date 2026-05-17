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

st.title("🏰 天堂血盟 - 行政秘書免費 AI 網頁系統 V16")

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
            img_preview = Image.open(io.BytesIO(file_bytes))
            st.image(img_preview, caption=f"圖片 {idx+1}", use_container_width=True)

# =====================================================================
# 5. 鋼鐵律令提示詞
# =====================================================================
PROMPT_TEMPLATE = """
你現在是《天堂》遊戲的血盟行政秘書。這張圖片是隊伍名單截圖。
請你直奔「左下角隊伍 UI 區」，完全忽略右側聊天室（例如淡水柯景騰等雜訊）。

請嚴格、逐字對照以下【神盛核心白名單】：
什麼漾子、湊人數、和尚洗髮水、煙雨遙運行、小熊闖天下、波波鼠、筱駱駱、佛、紫楓秋夜、大都督、一小法一、蘇州賣鴨蛋、霸气小君、霸氣小君、天降神運、齊、粉色紅頭龜、飛翔的企鵝、168、紅心皇后、跑皮達人、柯基、粉色KITTY、夜駱駝。

【👑 鐵律：隊長特別注意】
小隊的第一個名字（最上方的名字）是隊長。
1. 當你看到只有單一個字「齊」在隊伍最上方時，他就是隊長！絕對不要漏掉他、也不要用下面的名字取代他！
2. 「什麼漾子」、「筱駱駱」、「齊」這三個人只要出現在小隊中，他們必然是他們那張圖的隊長，必須排在第一行。

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
# 6. 操作按鈕功能區
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    execute_click = st.button("🔥 執行 100% 免費大模型精準名單認列", use_container_width=True)

with btn_col2:
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
        
        # 🌟 建立專門為了 Excel 7大欄位設計的複製字串 (用 \t 完美分隔行與列)
        raw_text_report = ""
        
        # 網頁端的圖形化精美顯示
        report_html = f"""
        <div class='report-box'>
            <span style='color: #2ecc71; font-weight: bold; font-size: 18px;'>✨ 已為您讀取並認列此場次的隊員名單：</span><br>
            <div style='font-size: 15px; margin: 10px 0 20px 0; line-height:1.5;'>
                <b>場次資訊</b><br>
                • 日期: {date_str}<br>
                • 時間: {selected_time}<br>
                • 出團目標: {selected_target}<br>
                • 指揮官：{selected_commander}
            </div>
        """
        
        global_member_idx = 1 # 打散全圖後的流水號
        
        for idx, file in enumerate(uploaded_files, start=1):
            file.seek(0)
            file_bytes = file.read()
            pil_image = Image.open(io.BytesIO(file_bytes))
            
            try:
                response = model.generate_content([PROMPT_TEMPLATE, pil_image])
                ai_output = response.text
                lines = ai_output.strip().split('\n')
                
                report_html += f"<span class='img-title'>📸 圖片 {idx} ({file.name}) 名單：</span><br>"
                
                for line in lines:
                    clean_line = line.replace("[LEADER]", "").replace("[MEMBER]", "").replace("•", "").strip()
                    name_only = clean_line.split("(")[0].strip()
                    
                    if name_only in VALID_NAMES:
                        # 🌟 核心公式：序號 \t 日期 \t 時間 \t 出團目標 \t 指揮官 \t 成員名單 \t 職位
                        excel_row_base = f"{global_member_idx}\t{date_str}\t{selected_time}\t{selected_target}\t{selected_commander}\t{name_only}"
                        
                        if name_only in ["什麼漾子", "筱駱駱", "齊"] or "(隊長)" in clean_line:
                            if name_only == "什麼漾子":
                                report_html += f"<div class='leader-y'>{global_member_idx}. {name_only} (隊長)</div>"
                            else:
                                report_html += f"<div class='leader-o'>{global_member_idx}. {name_only} (隊長)</div>"
                            raw_text_report += f"{excel_row_base}\t隊長\n"
                        else:
                            report_html += f"<div class='member-w'>{global_member_idx}. {name_only}</div>"
                            raw_text_report += f"{excel_row_base}\t\n" # 隊員職位留空
                        
                        global_member_idx += 1
                        
            except Exception as e:
                st.error(f"圖片 {idx} 辨識出錯：{e}")
                
        report_html += "</div>"
        
        # 1. 網頁渲染
        st.markdown(report_html, unsafe_allow_html=True)
        
        # 2. 顯示純文字框
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_area("📋 下方為專用 Excel 貼上格式數據（7大欄位）：", value=raw_text_report.strip(), height=250, key="copy_target")
        
        # 3. 原生 JavaScript 一鍵複製大按鈕
        escaped_text = raw_text_report.strip().replace("`", "\\`").replace("'", "\\'")
        js_button_html = f"""
        <div style="text-align: center; width: 100%;">
            <button onclick="navigator.clipboard.writeText(`{escaped_text}`).then(() => alert('📋 報告老大：7大欄位專用數據已複製！可直接前往 Excel 的 A1 儲存格貼上。'));" 
            style="width: 100%; background-color: #16a085; color: white; border: none; padding: 15px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                📋 點我一鍵複製 Excel 7大欄位數據
            </button>
        </div>
        """
        st.components.v1.html(js_button_html, height=70)
