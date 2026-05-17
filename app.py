import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import datetime
import itertools

# =====================================================================
# 1. 狂盟尊爵：天堂經典血誓不朽視覺風格 (CSS 究極魔改版)
# =====================================================================
st.markdown("""
    <style>
    /* 全局戰場黑背景 */
    .main { 
        background-color: #0a0a0b; 
        color: #e6e6e6; 
        font-family: 'Microsoft JhengHei', 'Segoe UI', sans-serif; 
    }
    
    /* 側邊欄黑鐵化 */
    [data-testid="stSidebar"] {
        background-color: #111113 !important;
        border-right: 1px solid #443615;
    }
    
    /* 狂盟烈焰血紅大標題 */
    .clan-title { 
        color: #b30000; 
        text-align: center; 
        font-weight: 900; 
        font-size: 32px;
        text-shadow: 3px 3px 6px #000000, 0 0 15px #b30000; 
        letter-spacing: 3px;
        padding: 10px 0;
        border-bottom: 2px dashed #b30000;
        margin-bottom: 25px;
    }
    
    /* 皇家暗金不朽邊框報告箱 */
    .report-box { 
        background-color: #121215; 
        border: 2px solid #9a7b2c; 
        padding: 25px; 
        border-radius: 6px; 
        box-shadow: 0 5px 15px rgba(0,0,0,0.8), inset 0 0 15px rgba(0,0,0,0.6); 
    }
    
    /* 資訊小標題 */
    .info-title {
        color: #9a7b2c;
        font-size: 16px;
        font-weight: bold;
        border-left: 4px solid #b30000;
        padding-left: 8px;
        margin-bottom: 15px;
    }
    
    /* 圖片小隊標題藍 */
    .img-title { 
        color: #3a86c8; 
        font-weight: bold; 
        font-size: 16px; 
        margin-top: 25px; 
        display: block; 
        text-shadow: 1px 1px 2px #000;
    }
    
    /* 狂盟主力隊長黃金字 */
    .leader-y { 
        color: #ffcc00; 
        font-weight: bold; 
        padding-left: 15px; 
        font-size: 16px; 
        text-shadow: 1px 1px 2px #000;
        margin: 5px 0;
    }
    
    /* 狂盟突擊隊長烈橘字 */
    .leader-o { 
        color: #e66b00; 
        font-weight: bold; 
        padding-left: 15px; 
        font-size: 16px; 
        text-shadow: 1px 1px 2px #000;
        margin: 5px 0;
    }
    
    /* 狂盟鋼鐵戰員象牙白字 */
    .member-w { 
        color: #dfdfdf; 
        padding-left: 15px; 
        margin: 4px 0; 
        font-size: 15px; 
    }
    
    /* 強制修改 Streamlit 內建標籤顏色為暗金 */
    label { 
        color: #9a7b2c !important; 
        font-weight: bold !important; 
        font-size: 14px !important;
    }
    
    /* 輸入框黑框化 */
    input, select, div[data-baseweb="select"] {
        background-color: #16161a !important;
        color: #ffffff !important;
        border: 1px solid #443615 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 狂盟專屬血契大標題
st.markdown("<div class='clan-title'>🏰 狂盟戰盟 - 行政秘書免費 AI 點名系統 V18</div>", unsafe_allow_html=True)

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

if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# =====================================================================
# 3. 前端選單輸入區
# =====================================================================
api_key = st.sidebar.text_input("🔑 輸入 Google Gemini API Key:", type="password")

st.markdown("<div class='info-title'>⚔️ 狂盟參戰戰報設定</div>", unsafe_allow_html=True)

col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input("📅 選擇作戰日期:", datetime.date(2026, 5, 17))
with col_time:
    time_options = [f"{str(h).zfill(2)}00" for h in range(24)]
    selected_time = st.selectbox("⏰ 選擇出兵時間 (整點):", options=time_options, index=8)

col_target, col_cmd = st.columns(2)
with col_target:
    selected_target = st.selectbox("🎯 鎖定出團目標:", options=all_combinations)
with col_cmd:
    selected_commander = st.selectbox("👑 當場統帥指揮官:", options=COMMANDER_LIST, index=0)

st.markdown("<hr style='border:0.5px solid #332707;'>", unsafe_allow_html=True)

# 上傳元件
uploaded_files = st.file_uploader(
    "📸 請拖曳或上傳戰場隊伍截圖 (可多選)", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg'],
    key=f"uploader_{st.session_state.uploader_key}"
)

# 🔒 安全防呆鎖邏輯
is_uploading = False
if uploaded_files:
    st.markdown("<b style='color:#3a86c8;'>🖼️ 戰場截圖預覽 (確認無誤後再點火執行)：</b>", unsafe_allow_html=True)
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, file in enumerate(uploaded_files):
        with cols[idx % 4]:
            file_bytes = file.read()
            file.seek(0)
            if len(file_bytes) == 0:
                is_uploading = True
            img_preview = Image.open(io.BytesIO(file_bytes))
            st.image(img_preview, caption=f"截圖 {idx+1}", use_container_width=True)

# =====================================================================
# 4. 操作按鈕功能區 (防呆按鈕鎖死機制)
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if is_uploading:
        st.button("⏳ 戰場影像讀取中，冷卻中...", disabled=True, use_container_width=True)
        execute_click = False
    else:
        # 使用自定義風格按鈕 (紅色點火)
        execute_click = st.button("🔥 點火！發動 AI 陣營精準名單審查", use_container_width=True)

with btn_col2:
    if is_uploading:
        st.button("🔄 熔爐清理鎖定中", disabled=True, use_container_width=True)
    else:
        if st.button("🔄 戰報重置 / 準備下一場戰役", use_container_width=True):
            st.session_state.uploader_key += 1
            st.rerun()

# =====================================================================
# 5. 鋼鐵律令提示詞
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
# 6. 核心處理與報告輸出
# =====================================================================
if execute_click:
    if not api_key:
        st.error("⚠️ 老大，請先在左側邊欄填入您的 Google API 金鑰喔！")
    elif uploaded_files:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        date_str = selected_date.strftime("%Y%m%d")
        raw_text_report = ""
        
        # 網頁端狂盟殿堂排版
        report_html = f"""
        <div class='report-box'>
            <span style='color: #b30000; font-weight: bold; font-size: 18px;'>✨ 狂盟出征 - 隊員名單審查完畢：</span><br>
            <div style='font-size: 15px; margin: 12px 0 25px 0; line-height:1.6; border-bottom: 1px solid #443615; padding-bottom: 10px;'>
                <b style='color: #9a7b2c;'>【戰役基本資訊】</b><br>
                • ⚔️ 作戰日期: {date_str}<br>
                • ⏰ 出兵時間: {selected_time}<br>
                • 🎯 戰術目標: {selected_target}<br>
                • 👑 戰場統帥: {selected_commander}
            </div>
        """
        
        global_excel_idx = 1
        has_any_data = False
        
        for idx, file in enumerate(uploaded_files, start=1):
            file.seek(0)
            file_bytes = file.read()
            pil_image = Image.open(io.BytesIO(file_bytes))
            
            try:
                response = model.generate_content([PROMPT_TEMPLATE, pil_image])
                ai_output = response.text
                lines = ai_output.strip().split('\n')
                
                report_html += f"<span class='img-title'>📸 戰術分隊 {idx} ({file.name})：</span><br>"
                local_team_idx = 1 
                
                for line in lines:
                    clean_line = line.replace("[LEADER]", "").replace("[MEMBER]", "").replace("•", "").strip()
                    name_only = clean_line.split("(")[0].strip()
                    
                    # 👑 齊老大核心特赦鎖（杜絕漏人）
                    if "齊" in clean_line and name_only not in VALID_NAMES:
                        name_only = "齊"
                    
                    if name_only in VALID_NAMES:
                        has_any_data = True
                        excel_row_base = f"{global_excel_idx}\t{date_str}\t{selected_time}\t{selected_target}\t{selected_commander}\t{name_only}"
                        
                        if name_only in ["什麼漾子", "筱駱駱", "齊"] or "(隊長)" in clean_line or "[LEADER]" in line:
                            if name_only == "什麼漾子":
                                report_html += f"<div class='leader-y'>{local_team_idx}. ⚔️ {name_only} (隊長)</div>"
                            else:
                                report_html += f"<div class='leader-o'>{local_team_idx}. ⚔️ {name_only} (隊長)</div>"
                            raw_text_report += f"{excel_row_base}\t隊長\n"
                        else:
                            report_html += f"<div class='member-w'>{local_team_idx}. {name_only}</div>"
                            raw_text_report += f"{excel_row_base}\t\n"
                        
                        local_team_idx += 1
                        global_excel_idx += 1
                        
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    st.error(f"❌ 限制：當前 Google 金鑰免費額度乾涸！請至左側欄換上預備金鑰。")
                else:
                    st.error(f"❌ 戰場影像 {idx} 讀取挫敗：{e}")
                
        report_html += "</div>"
        
        # 渲染狂盟殿堂報告
        st.markdown(report_html, unsafe_allow_html=True)
        
        # 只要有數據，就強制解鎖釋放數據框
        if has_any_data:
            st.markdown("<br>", unsafe_allow_html=True)
            st.text_area("📋 狂盟專用 Excel 數據分流（複製此處直貼 A1）：", value=raw_text_report.strip(), height=250, key="copy_target")
            
            escaped_text = raw_text_report.strip().replace("`", "\\`").replace("'", "\\'")
            js_button_html = f"""
            <div style="text-align: center; width: 100%;">
                <button onclick="navigator.clipboard.writeText(`{escaped_text}`).then(() => alert('📋 報告老大：狂盟發餉戰報複製成功！請至 Excel 貼上。'));" 
                style="width: 100%; background-color: #b30000; color: white; border: 2px solid #9a7b2c; padding: 16px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; box-shadow: 0 4px 10px rgba(179,0,0,0.4);">
                    🦅 複製狂盟戰盟 7 大欄位數據 🦅
                </button>
            </div>
            """
            st.components.v1.html(js_button_html, height=75)
        else:
            st.warning("⚔️ 未能擷取到任何有效的戰盟成員數據，請確認金鑰是否過期。")
