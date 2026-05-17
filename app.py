import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import datetime
import itertools
import time

# 配置網頁分頁標題與圖示
st.set_page_config(page_title="狂盟血盟後台系統", page_icon="🏰", layout="wide")

# =====================================================================
# 1. 狂盟尊爵：天堂經典血誓不朽視覺風格 (CSS 究極魔改 V26 版)
# =====================================================================
st.markdown("""
    <style>
    /* 全局戰場迷霧深黑 */
    .main { 
        background-color: #060608; 
        color: #e5e5e7; 
        font-family: 'Microsoft JhengHei', 'Segoe UI', sans-serif; 
    }
    
    /* 側邊欄高端鐵冷色 */
    [data-testid="stSidebar"] {
        background-color: #0b0b0d !important;
        border-right: 3px solid #d4af37;
    }
    
    /* 標題區：狂盟血誓神殿大門 */
    .clan-header {
        background: linear-gradient(135deg, rgba(179,0,0,0.3) 0%, rgba(10,10,12,0.9) 50%, rgba(154,123,44,0.15) 100%);
        border: 2px solid #d4af37;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 0 25px rgba(255,0,0,0.35), inset 0 0 20px rgba(212,175,55,0.1);
    }
    .clan-title { 
        color: #ff0000; 
        font-weight: 900; 
        font-size: 40px;
        text-shadow: 3px 3px 6px #000000, 0 0 30px #ff0000, 0 0 10px #ffffff; 
        letter-spacing: 5px;
        margin: 0;
    }
    .clan-subtitle {
        color: #d4af37;
        font-size: 15px;
        letter-spacing: 3px;
        margin-top: 8px;
        font-weight: bold;
        text-shadow: 1px 1px 2px #000;
    }
    
    /* 皇家暗金立體報告箱 */
    .report-box { 
        background: linear-gradient(145deg, #0f0f12, #15151a);
        border: 2px solid #d4af37; 
        padding: 35px; 
        border-radius: 10px; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.9), 0 0 20px rgba(212,175,55,0.15);
    }
    
    /* 區塊核心發光標題 */
    .section-tag {
        color: #ffffff;
        font-size: 19px;
        font-weight: bold;
        background: linear-gradient(90deg, #b30000 0%, rgba(179,0,0,0.1) 70%, transparent 100%);
        padding: 8px 18px;
        border-radius: 4px;
        margin-bottom: 22px;
        border-left: 6px solid #ff0000;
        text-shadow: 1px 1px 3px #000;
    }
    
    /* 圖片分隊卡片 */
    .img-title { 
        color: #ffcc00; 
        font-weight: bold; 
        font-size: 17px; 
        margin-top: 28px; 
        display: block;
        border-bottom: 2px solid #443615;
        padding-bottom: 6px;
    }
    
    /* 👑 隊長一律顯示為爆擊橘色 */
    .leader-orange { 
        color: #ff4500 !important; 
        font-weight: bold !important; 
        padding-left: 20px; 
        font-size: 17px; 
        margin: 8px 0; 
        text-shadow: 1px 1px 4px #000; 
    }
    .member-w { color: #e5e5e7; padding-left: 20px; margin: 6px 0; font-size: 16px; }
    
    /* 修改所有預設 Label 顏色為不朽金 */
    label { 
        color: #d4af37 !important; 
        font-weight: bold !important; 
        font-size: 16px !important;
        letter-spacing: 1px;
        text-shadow: 1px 1px 2px #000;
        margin-bottom: 8px !important;
    }
    
    /* 🛠️ 下拉選單與輸入框徹底移除游標小框框 🛠️ */
    input, select, div[data-baseweb="select"], div[data-baseweb="input"], .stSelectbox, .stDateInput {
        background-color: #111114 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div[data-baseweb="select"] {
        border: 1px solid #d4af37 !important;
    }
    input {
        border: 1px solid #d4af37 !important;
        caret-color: transparent !important; /* 強制關閉任何閃爍小框框 */
    }
    
    div[data-baseweb="select"]:focus-within, div[data-baseweb="input"]:focus-within, input:focus {
        border-color: #ff0000 !important;
        box-shadow: 0 0 14px rgba(255,0,0,0.7) !important;
    }
    
    div[data-testid="stFileUploader"] {
        background-color: #0b0b0d;
        border: 2px dashed #b30000 !important;
        border-radius: 10px;
        padding: 15px;
    }
    
    /* 💥 雙核心按鈕控制台樣式魔改 */
    div.stButton > button[key="attack_btn"] {
        background: linear-gradient(180deg, #ff0000 0%, #aa0000 50%, #660000 100%) !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        border: 2px solid #ffcc00 !important;
        box-shadow: 0 0 20px rgba(255,0,0,0.7), inset 0 0 10px rgba(255,255,255,0.3) !important;
        text-shadow: 2px 2px 5px #000000, 0 0 10px #ff0000 !important;
        letter-spacing: 3px !important;
        transition: all 0.2s ease !important;
        height: 65px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
    }
    div.stButton > button[key="attack_btn"]:hover {
        background: linear-gradient(180deg, #ff3333 0%, #cc0000 50%, #880000 100%) !important;
        box-shadow: 0 0 35px rgba(255,0,0,1), 0 0 15px #ffcc00 !important;
        transform: scale(1.01) translateY(-2px);
    }
    
    div.stButton > button[key="reset_btn"] {
        background: linear-gradient(180deg, #333338 0%, #1c1c1f 50%, #0d0d0f 100%) !important;
        color: #d4af37 !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        border: 2px solid #554518 !important;
        text-shadow: 2px 2px 3px #000000 !important;
        letter-spacing: 2px !important;
        transition: all 0.2s ease !important;
        height: 65px !important;
        border-radius: 8px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5) !important;
        cursor: pointer !important;
    }
    div.stButton > button[key="reset_btn"]:hover {
        background: linear-gradient(180deg, #44444a 0%, #29292e 50%, #16161a 100%) !important;
        color: #ffffff !important;
        border-color: #d4af37 !important;
        box-shadow: 0 0 20px rgba(212,175,55,0.4) !important;
        transform: scale(1.01) translateY(-2px);
    }
    
    /* 👑 簡約風黑金鋼鐵戰術欄位示意表格 */
    .clan-table-container {
        margin-top: 5px;
        margin-bottom: 5px;
        border: 1px solid #d4af37;
        border-radius: 4px;
        overflow: hidden;
    }
    .clan-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #0c0c0e;
        text-align: center;
    }
    .clan-table th {
        background: linear-gradient(180deg, #1a1a1e 0%, #0d0d10 100%);
        color: #d4af37;
        font-weight: bold;
        font-size: 14px;
        padding: 8px;
        border-bottom: 1px solid #33270c;
        border-right: 1px solid #221a08;
        letter-spacing: 2px;
    }
    .clan-table th:last-child {
        border-right: none;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. 核心機制：金鑰與上傳鎖
# =====================================================================
if 'saved_api_key' not in st.session_state:
    st.session_state.saved_api_key = ""

if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# =====================================================================
# 3. 戰略操作介面
# =====================================================================
st.markdown("""
    <div class='clan-header'>
        <div class='clan-title'>🏰 狂盟血誓戰盟 - 頂級 AI 戰略行政系統 V26</div>
        <div class='clan-subtitle'>COMMAND CENTER • FOR INTERNAL USE OF CLAN LEADERS ONLY</div>
    </div>
""", unsafe_allow_html=True)

api_key = st.sidebar.text_input("🔑 狂盟核心 API 認證金鑰：", value=st.session_state.saved_api_key, type="password")
if api_key:
    st.session_state.saved_api_key = api_key

st.markdown("<div class='section-tag'>⚔️ 戰報參數設定儀表板</div>", unsafe_allow_html=True)

base_targets = ["四色", "飛龍", "伊佛", "蟻媽媽", "克特", "掃街", "打架"]
all_combinations = []
for r in range(1, len(base_targets) + 1):
    for combo in itertools.combinations(base_targets, r):
        all_combinations.append("+".join(combo))
if "飛龍+四色+伊佛" in all_combinations:
    all_combinations.remove("飛龍+四色+伊佛")
all_combinations.insert(0, "飛龍+四色+伊佛")

COMMANDER_LIST = ["齊", "什麼漾子", "筱駱駱", "夜駱駝", "大都督", "副盟主1", "副盟主2"]
time_options = [f"{str(h).zfill(2)}00" for h in range(24)]

col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input("📅 戰役發動日期:", datetime.date(2026, 5, 17))
with col_time:
    selected_time = st.selectbox("⏰ 吹哨集結時間 (整點):", options=time_options, index=8)

col_target, col_cmd = st.columns(2)
with col_target:
    selected_target = st.selectbox("🎯 征討核心目標:", options=all_combinations)
with col_cmd:
    selected_commander = st.selectbox("👑 戰場最高統帥指揮官:", options=COMMANDER_LIST, index=0)

st.markdown("<br><div class='section-tag'>📸 戰場軍情影像熔爐</div>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "請將本次戰役的所有小隊截圖拖曳至此：", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg'],
    key=f"uploader_{st.session_state.uploader_key}"
)

is_uploading = False
if uploaded_files:
    st.markdown("<b style='color:#3a86c8;'>🖼️ 戰場核心影像載入預覽：</b>", unsafe_allow_html=True)
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, file in enumerate(uploaded_files):
        with cols[idx % 4]:
            file_bytes = file.read()
            file.seek(0)
            if len(file_bytes) == 0:
                is_uploading = True
            img_preview = Image.open(io.BytesIO(file_bytes))
            st.image(img_preview, caption=f"軍情圖片 {idx+1}", use_container_width=True)

# =====================================================================
# 4. 操作控制台 (雙核心究極震撼按鈕)
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if is_uploading:
        st.markdown("""
            <button style="width: 100%; background-color: #222; color: #ff0000; border: 1px solid #ff0000; padding: 12px; font-weight: bold; border-radius: 4px; cursor: not-allowed; animation: blinker 1.5s linear infinite; height:65px;">
                ⏳ 戰術分隊影像校閱中...請稍後點火
            </button>
            <style>@keyframes blinker { 50% { opacity: 0.3; } }</style>
        """, unsafe_allow_html=True)
        execute_click = False
    else:
        execute_click = st.button("🔥 發動總攻擊！啟動狂盟核心點名認列", key="attack_btn", use_container_width=True)

with btn_col2:
    if is_uploading:
        pass
    else:
        if st.button("🔄 熔爐重置 / 清理當前戰報準備下一場", key="reset_btn", use_container_width=True):
            st.session_state.uploader_key += 1
            st.rerun()

# =====================================================================
# 5. 🎯 100% 視覺特化核心提示詞
# =====================================================================
PROMPT_TEMPLATE = """
你現在是《天堂》遊戲的血盟行政秘書。請精準分析這張小隊截圖。
請把所有焦點集中在「圖片左下角的藍色隊伍名單 UI 區塊」，完全忽略右邊聊天室等雜訊。

請拿出放大鏡，將左下角隊伍 UI 的每一行文字由上到下，逐字與以下【白名單】核對：
什麼漾子、湊人數、和尚洗髮水、煙雨遙、小熊闖天下、波波鼠、筱駱駱、佛、紫楓秋夜、大都督、一小法一、蘇州賣鴨蛋、霸气小君、霸氣小君、天降神運、齊、粉色紅頭龜、飛翔的企鵝、168、紅心皇后、跑皮達人、柯基、粉色KITTY、夜駱駝。

【👑 隊長階級精準判定鐵律】：
1. 隊伍最上面第一行的名字，正前方一定會黏著一個黃金色的隊長皇冠（👑）圖標。
2. 因為圖標干擾或名字只有一個字（例如單字「齊」），這會導致字元邊緣被皇冠切到。請特別注意：不論它前後夾帶什麼符號或空格，只要包含白名單的名字，就必須精準擷取！
3. 請確保排在最上方第一行的那個人，不論他是誰，他就是該分隊的「隊長」。

【精準輸出格式】：
不要回答任何說明廢話，只輸出以下格式：
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
        st.error("⚠️ 老大！請先在左側邊欄鎖定您的 狂盟核心 API 金鑰！")
    elif uploaded_files:
        time.sleep(0.5)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        date_str = selected_date.strftime("%Y%m%d")
        raw_text_report = ""
        
        # 🌟 老大指令：最前方的 • 符號已全部斬斷，畫面極致乾淨 🌟
        report_html = f"""
        <div class='report-box'>
            <div class='section-tag' style='background:none; border:none; padding:0; color:#ff0000; font-size:20px;'>🦅 狂盟點名大會師 - 成果報告庫</div>
            <div style='font-size: 15px; margin: 15px 0 25px 0; line-height:1.6; border-bottom: 1px solid #443615; padding-bottom: 15px;'>
                <b style='color: #d4af37; font-size:16px;'>【本次戰報核心資訊】</b><br>
                戰役日期: <span style='color:#fff; font-weight:bold;'>{date_str}</span><br>
                吹哨時間: <span style='color:#fff; font-weight:bold;'>{selected_time}</span><br>
                征討目標: <span style='color:#ffcc00; font-weight:bold;'>{selected_target}</span><br>
                最高統帥: <span style='color:#ff0000; font-weight:bold;'>{selected_commander}</span>
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
                    # 🌟 核心升級：全面採用「子字串包含比對」防止空格與雜訊造成比對失敗 🌟
                    matched_name = None
                    for v_name in VALID_NAMES:
                        if v_name in line:  # 只要該行包含白名單名字
                            matched_name = v_name
                            break
                    
                    if matched_name:
                        has_any_data = True
                        excel_row_base = f"{global_excel_idx}\t{date_str}\t{selected_time}\t{selected_target}\t{selected_commander}\t{matched_name}"
                        
                        # 只要是該小隊分析出來的第一行，或者是大模型標註的 LEADER，一律認定為隊長
                        is_leader = "[LEADER]" in line or "(隊長)" in line or local_team_idx == 1
                        
                        if is_leader:
                            # 🌟 老大指令：隊長一律顯示為橘色高亮 (#ff4500) 🌟
                            report_html += f"<div class='leader-orange'>{local_team_idx}. 🎖️ {matched_name} (隊長)</div>"
                            raw_text_report += f"{excel_row_base}\t隊長\n"
                        else:
                            report_html += f"<div class='member-w'>{local_team_idx}. {matched_name}</div>"
                            raw_text_report += f"{excel_row_base}\t\n"
                        
                        local_team_idx += 1
                        global_excel_idx += 1
                        
            except Exception as e:
                st.error(f"❌ 軍情影像 {idx} 處理失敗：{e}")
                
        report_html += "</div>"
        st.markdown(report_html, unsafe_allow_html=True)
        
        if has_any_data:
            st.markdown("<br><div class='section-tag'>📋 狂盟直貼 Excel 數據中心 (完美相容 7 大直欄)</div>", unsafe_allow_html=True)
            
            # 🌟 老大指定排版：提示語 -> 黑金示意表格 -> 數據框 🌟
            st.markdown("<b style='color:#ffffff; font-size:15px;'>請直接對下方框內全選複製 (Ctrl+A → Ctrl+C)：</b>", unsafe_allow_html=True)
            
            # 簡約風黑金戰術欄位示意表格
            st.markdown("""
                <div class='clan-table-container'>
                    <table class='clan-table'>
                        <thead>
                            <tr>
                                <th>序號</th>
                                <th>日期</th>
                                <th>時間</th>
                                <th>出團目標</th>
                                <th>指揮官</th>
                                <th>成員名單</th>
                                <th>職位</th>
                            </tr>
                        </thead>
                    </table>
                </div>
            """, unsafe_allow_html=True)
            
            # 數據顯示文字框
            st.text_area("", value=raw_text_report.strip(), height=250, key="copy_target", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            
            escaped_text = raw_text_report.strip().replace("`", "\\`").replace("'", "\\'")
            js_button_html = f"""
            <div style="text-align: center; width: 100%;">
                <button onclick="navigator.clipboard.writeText(`{escaped_text}`).then(() => alert('📋 報告老大：狂盟頂級數據已完美複製！請至 Excel 貼上。'));" 
                style="width: 100%; background: linear-gradient(180deg, #cc0000 0%, #880000 100%); color: white; border: 2px solid #d4af37; padding: 18px; font-size: 18px; font-weight: bold; border-radius: 6px; cursor: pointer; box-shadow: 0 6px 15px rgba(255,0,0,0.4); text-shadow: 1px 1px 3px #000; letter-spacing:2px;">
                    🦅 一鍵秒複製 7 大欄位狂盟核心數據 🦅
                </button>
            </div>
            """
            st.components.v1.html(js_button_html, height=80)
        else:
            st.warning("⚔️ 未能擷取到任何有效的戰盟成員數據，請確認金鑰是否過期。")
