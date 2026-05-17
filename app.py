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
# 1. 狂盟尊爵：天堂經典血誓不朽視覺風格 (CSS 究極魔改 V22 版)
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
    
    /* 隊長與隊員字體升級 */
    .leader-y { color: #ff9900; font-weight: bold; padding-left: 20px; font-size: 17px; margin: 8px 0; text-shadow: 1px 1px 4px #000; }
    .leader-o { color: #ff4500; font-weight: bold; padding-left: 20px; font-size: 17px; margin: 8px 0; text-shadow: 1px 1px 4px #000; }
    .member-w { color: #e5e5e7; padding-left: 20px; margin: 6px 0; font-size: 16px; }
    
    /* 修改所有預設 Label 顏色為不朽金 */
    label { 
        color: #d4af37 !important; 
        font-weight: bold !important; 
        font-size: 15px !important;
        letter-spacing: 1px;
        text-shadow: 1px 1px 2px #000;
    }
    
    /* 🛠️ 核心修正：輸入框與下拉選單徹底隱藏直條游標 🛠️ */
    input, select, div[data-baseweb="select"], div[data-baseweb="input"] {
        background-color: #111114 !important;
        color: #ffffff !important;
        border: 1px solid #d4af37 !important;
        border-radius: 6px !important;
        transition: all 0.3s ease-in-out !important;
        caret-color: transparent !important; /* 🔥 徹底消滅游標小框框 */
    }
    
    /* 滑鼠移入輸入框爆發血光特效 */
    input:focus, div[data-baseweb="select"]:focus, div[data-baseweb="input"]:focus-within {
        border-color: #ff0000 !important;
        box-shadow: 0 0 12px rgba(255,0,0,0.6) !important;
    }
    
    /* 客製化：上傳檔案區魔改 */
    div[data-testid="stFileUploader"] {
        background-color: #0b0b0d;
        border: 2px dashed #b30000 !important;
        border-radius: 10px;
        padding: 15px;
    }
    
    /* 💥 狂盟專屬雙核狂化按鈕控制台樣式 */
    div.stButton > button[key="attack_btn"] {
        background: linear-gradient(180deg, #ff0000 0%, #880000 100%) !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        border: 2px solid #d4af37 !important;
        box-shadow: 0 0 18px rgba(255,0,0,0.6) !important;
        text-shadow: 2px 2px 4px #000000 !important;
        letter-spacing: 2px !important;
        transition: all 0.2s ease !important;
        height: 60px !important;
        border-radius: 6px !important;
    }
    div.stButton > button[key="attack_btn"]:hover {
        background: linear-gradient(180deg, #ff3333 0%, #aa0000 100%) !important;
        box-shadow: 0 0 28px rgba(255,0,0,0.95) !important;
        transform: translateY(-2px);
    }
    
    div.stButton > button[key="reset_btn"] {
        background: linear-gradient(180deg, #2a2a2e 0%, #141416 100%) !important;
        color: #d4af37 !important;
        font-weight: bold !important;
        font-size: 17px !important;
        border: 1px solid #443615 !important;
        text-shadow: 1px 1px 3px #000000 !important;
        letter-spacing: 1px !important;
        transition: all 0.2s ease !important;
        height: 60px !important;
        border-radius: 6px !important;
    }
    div.stButton > button[key="reset_btn"]:hover {
        background: linear-gradient(180deg, #3a3a42 0%, #1f1f23 100%) !important;
        color: #ffcc00 !important;
        border-color: #d4af37 !important;
        box-shadow: 0 0 15px rgba(212,175,55,0.3) !important;
    }
    
    /* 專用 Excel 欄位對位引導盒 */
    .excel-guideline-box {
        background-color: #0a0a0d;
        border: 1px solid #443615;
        border-radius: 6px;
        padding: 15px 25px;
        margin-top: -12px;
        margin-bottom: 25px;
        box-shadow: inset 0 0 10px #000;
    }
    .excel-guideline-item {
        display: inline-block;
        margin-right: 25px;
        font-size: 14px;
        font-family: 'Courier New', monospace;
    }
    .guideline-letter { color: #ffcc00; font-weight: bold; }
    .guideline-text { color: #a0a0a0; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. 核心機制：金鑰自動記憶功能 (Session State 機制)
# =====================================================================
if 'saved_api_key' not in st.session_state:
    st.session_state.saved_api_key = ""

if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# =====================================================================
# 3. 狂盟大門 - 戰略操作介面
# =====================================================================
st.markdown("""
    <div class='clan-header'>
        <div class='clan-title'>🏰 狂盟血誓戰盟 - 頂級 AI 戰略行政系統 V22</div>
        <div class='clan-subtitle'>COMMAND CENTER • FOR INTERNAL USE OF CLAN LEADERS ONLY</div>
    </div>
""", unsafe_allow_html=True)

api_key = st.sidebar.text_input(
    "🔑 狂盟核心 API 認證金鑰：", 
    value=st.session_state.saved_api_key, 
    type="password",
    help="輸入一次後系統將自動鎖定記憶，無須重複輸入。"
)

if api_key:
    st.session_state.saved_api_key = api_key

st.markdown("<div class='section-tag'>⚔️ 戰報參數設定儀表板</div>", unsafe_allow_html=True)

# 行動目標組合生成
base_targets = ["四色", "飛龍", "伊佛", "蟻媽媽", "克特", "掃街", "打架"]
all_combinations = []
for r in range(1, len(base_targets) + 1):
    for combo in itertools.combinations(base_targets, r):
        all_combinations.append("+".join(combo))
if "飛龍+四色+伊佛" in all_combinations:
    all_combinations.remove("飛龍+四色+伊佛")
all_combinations.insert(0, "飛龍+四色+伊佛")

COMMANDER_LIST = ["齊", "什麼漾子", "筱駱駱", "夜駱駝", "大都督", "副盟主1", "副盟主2"]

col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input("📅 戰役發動日期:", datetime.date(2026, 5, 17))
with col_time:
    time_options = [f"{str(h).zfill(2)}00" for h in range(24)]
    selected_time = st.selectbox("⏰ 吹哨集結時間 (整點):", options=time_options, index=8)

col_target, col_cmd = st.columns(2)
with col_target:
    selected_target = st.selectbox("🎯 征討核心目標:", options=all_combinations)
with col_cmd:
    selected_commander = st.selectbox("👑 戰場最高統帥指揮官:", options=COMMANDER_LIST, index=0)

st.markdown("<br><div class='section-tag'>📸 戰場軍情影像熔爐</div>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "請將本次戰役的所有小隊截圖拖曳至此，系統將啟動多線程軍情掃描：", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg'],
    key=f"uploader_{st.session_state.uploader_key}"
)

# 偵測圖片是否上傳完全與防呆
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
# 4. 操作控制台 (注入雙核心狂化按鈕 + 安全鎖防快取失效)
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if is_uploading:
        st.markdown("""
            <button style="width: 100%; background-color: #222; color: #ff0000; border: 1px solid #ff0000; padding: 12px; font-weight: bold; border-radius: 4px; cursor: not-allowed; animation: blinker 1.5s linear infinite; height:60px;">
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
        if st.button("☠️ 熔爐冷卻重置 / 掃除戰場殘骸", key="reset_btn", use_container_width=True):
            st.session_state.uploader_key += 1
            st.rerun()

# =====================================================================
# 5. 鋼鐵律令提示詞 (針對圖片3與齊老大強化壓制)
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
3. 特別注意：如果這張圖是【戰術分隊 3】，特別看清楚有沒有單字「齊」，他可能被黃色皇冠圖標擋到，無論如何都必須認列！

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
        st.error("⚠️ 老大！請先在左側邊欄鎖定您的 狂盟核心 API 金鑰！")
    elif uploaded_files:
        # 🛡️ 安全機制：在點火瞬間強制休息 0.5 秒，確保快取與 Streamlit 影像緩衝流完全同步
        time.sleep(0.5)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        date_str = selected_date.strftime("%Y%m%d")
        raw_text_report = ""
        
        report_html = f"""
        <div class='report-box'>
            <div class='section-tag' style='background:none; border:none; padding:0; color:#ff0000; font-size:20px;'>🦅 狂盟點名大會師 - 成果報告庫</div>
            <div style='font-size: 15px; margin: 15px 0 25px 0; line-height:1.6; border-bottom: 1px solid #443615; padding-bottom: 15px;'>
                <b style='color: #d4af37; font-size:16px;'>【本次戰報核心資訊】</b><br>
                • ⚔️ 征戰日期: <span style='color:#fff; font-weight:bold;'>{date_str}</span><br>
                • ⏰ 出兵時間: <span style='color:#fff; font-weight:bold;'>{selected_time}</span><br>
                • 🎯 戰術目標: <span style='color:#ffcc00; font-weight:bold;'>{selected_target}</span><br>
                • 👑 統帥指揮: <span style='color:#ff0000; font-weight:bold;'>{selected_commander}</span>
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
                    
                    # 👑 齊老大「不朽追蹤雷達」：只要行內有「齊」，不論前後有什麼皇冠，直接強制校正
                    if "齊" in clean_line:
                        name_only = "齊"
                    
                    if name_only in VALID_NAMES:
                        has_any_data = True
                        excel_row_base = f"{global_excel_idx}\t{date_str}\t{selected_time}\t{selected_target}\t{selected_commander}\t{name_only}"
                        
                        if name_only in ["什麼漾子", "筱駱駱", "齊"] or "(隊長)" in clean_line or "[LEADER]" in line:
                            if name_only == "什麼漾子":
                                report_html += f"<div class='leader-y'>{local_team_idx}. 🎖️ {name_only} (隊長)</div>"
                            else:
                                report_html += f"<div class='leader-o'>{local_team_idx}. 🎖️ {name_only} (隊長)</div>"
                            raw_text_report += f"{excel_row_base}\t隊長\n"
                        else:
                            report_html += f"<div class='member-w'>{local_team_idx}. {name_only}</div>"
                            raw_text_report += f"{excel_row_base}\t\n"
                        
                        local_team_idx += 1
                        global_excel_idx += 1
                        
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    st.error(f"❌ 警告：今日 Google 免費額度耗盡！請至左側更換新的金鑰。")
                else:
                    st.error(f"❌ 軍情影像 {idx} 掃描失敗：{e}")
                
        report_html += "</div>"
        
        st.markdown(report_html, unsafe_allow_html=True)
        
        if has_any_data:
            st.markdown("<br><div class='section-tag'>📋 狂盟直貼 Excel 數據中心 (完美相容 7 大直欄)</div>", unsafe_allow_html=True)
            st.text_area("請直接對下方框內全選複製 (Ctrl+A → Ctrl+C)：", value=raw_text_report.strip(), height=250, key="copy_target")
            
            # 欄位對位引導盒
            st.markdown("""
                <div class='excel-guideline-box'>
                    <span class='excel-guideline-item'><span class='guideline-letter'>[欄位 A]</span> <span class='guideline-text'>序號</span></span>
                    <span class='excel-guideline-item'><span class='guideline-letter'>[欄位 B]</span> <span class='guideline-text'>日期</span></span>
                    <span class='excel-guideline-item'><span class='guideline-letter'>[欄位 C]</span> <span class='guideline-text'>時間</span></span>
                    <span class='excel-guideline-item'><span class='guideline-letter'>[欄位 D]</span> <span class='guideline-text'>出團目標</span></span>
                    <span class='excel-guideline-item'><span class='guideline-letter'>[欄位 E]</span> <span class='guideline-text'>指揮官</span></span>
                    <span class='excel-guideline-item'><span class='guideline-letter'>[欄位 F]</span> <span class='guideline-text'>成員名單</span></span>
                    <span class='excel-guideline-item'><span class='guideline-letter'>[欄位 G]</span> <span class='guideline-text'>職位</span></span>
                </div>
            """, unsafe_allow_html=True)
            
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
