import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import datetime
import itertools
import time
import pandas as pd

# 配置網頁分頁標題與圖示
st.set_page_config(page_title="狂盟血盟後台系統", page_icon="🏰", layout="wide")

# =====================================================================
# 1. 狂盟尊爵：天堂經典血誓不朽視覺風格 (CSS 究極魔改 V32 版)
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
    
    /* 下拉選單與輸入框徹底移除游標小框框 */
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
        caret-color: transparent !important;
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
    
    /* 💥 雙核心按鈕控制台 */
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
    
    /* ⚡ 血誓不朽運算中動態等待框 ⚡ */
    .clan-loading-box {
        width: 100%;
        background: linear-gradient(135deg, #150505 0%, #080202 100%);
        border: 2px dashed #ff0000;
        padding: 18px;
        text-align: center;
        border-radius: 8px;
        box-shadow: 0 0 25px rgba(255,0,0,0.5);
        color: #ff3333;
        font-size: 18px;
        font-weight: bold;
        letter-spacing: 2px;
        animation: pulseBlinker 2s linear infinite;
        height: 65px;
        line-height: 25px;
    }
    @keyframes pulseBlinker {
        0% { opacity: 0.7; box-shadow: 0 0 15px rgba(255,0,0,0.3); }
        50% { opacity: 1.0; box-shadow: 0 0 30px rgba(255,0,0,0.8); color: #ff9999; }
        100% { opacity: 0.7; box-shadow: 0 0 15px rgba(255,0,0,0.3); }
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
# 2. 暫存機制初始化
# =====================================================================
if 'saved_api_key' not in st.session_state:
    st.session_state.saved_api_key = ""
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# 👑 秘書貼心鎖定：直接連結老大的雲端中央試算表
default_url_m = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQTnOiq6sWHfimLY5BTNOSf5pyXHNcymkxYHr2hyN8ChS0qBt3qCcldc3cdqJu7BXzjZccA8dpwIiah/pub?gid=0&single=true&output=csv"
default_url_t = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQTnOiq6sWHfimLY5BTNOSf5pyXHNcymkxYHr2hyN8ChS0qBt3qCcldc3cdqJu7BXzjZccA8dpwIiah/pub?gid=850131825&single=true&output=csv"
default_url_c = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQTnOiq6sWHfimLY5BTNOSf5pyXHNcymkxYHr2hyN8ChS0qBt3qCcldc3cdqJu7BXzjZccA8dpwIiah/pub?gid=110345115&single=true&output=csv"

if 'sheet_url_members' not in st.session_state:
    st.session_state.sheet_url_members = default_url_m
if 'sheet_url_targets' not in st.session_state:
    st.session_state.sheet_url_targets = default_url_t
if 'sheet_url_commanders' not in st.session_state:
    st.session_state.sheet_url_commanders = default_url_c

# =====================================================================
# 3. 側邊欄：🌐 Google Sheet 究極雲端自動化控制台
# =====================================================================
st.sidebar.markdown("<h3 style='color:#d4af37; text-align:center;'>🏰 神殿權限配置</h3>", unsafe_allow_html=True)
api_key = st.sidebar.text_input("🔑 核心 API 認證金鑰：", value=st.session_state.saved_api_key, type="password")
if api_key:
    st.session_state.saved_api_key = api_key

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#00ffcc; text-align:center;'>🌐 雲端連動設定中心</h3>", unsafe_allow_html=True)

url_m = st.sidebar.text_input("📋 1. 成員白名單 CSV 網址：", value=st.session_state.sheet_url_members)
url_t = st.sidebar.text_input("🎯 2. 出團目標 CSV 網址：", value=st.session_state.sheet_url_targets)
url_c = st.sidebar.text_input("👑 3. 指揮官名單 CSV 網址：", value=st.session_state.sheet_url_commanders)

if url_m: st.session_state.sheet_url_members = url_m.strip()
if url_t: st.session_state.sheet_url_targets = url_t.strip()
if url_c: st.session_state.sheet_url_commanders = url_c.strip()

# =====================================================================
# 4. 🔥 徹底鏟除測試資料：改為純淨實時雲端抓取機制
# =====================================================================
VALID_NAMES = []
base_targets = []
COMMANDER_LIST = []

# 動態抓取成員白名單
if st.session_state.sheet_url_members:
    try:
        df_m = pd.read_csv(st.session_state.sheet_url_members, header=None, encoding='utf-8')
        if not df_m.empty:
            raw_list = df_m.iloc[:, 0].dropna().astype(str).tolist()
            VALID_NAMES = [x.strip() for x in raw_list if x.strip() and x.strip() != "姓名"]
    except Exception as e:
        st.sidebar.error("⚠️ 無法讀取雲端成員名單，請確認網址。")

# 動態抓取王怪目標
if st.session_state.sheet_url_targets:
    try:
        df_t = pd.read_csv(st.session_state.sheet_url_targets, header=None, encoding='utf-8')
        if not df_t.empty:
            raw_list = df_t.iloc[:, 0].dropna().astype(str).tolist()
            base_targets = [x.strip() for x in raw_list if x.strip() and x.strip() != "目標"]
    except Exception as e:
        st.sidebar.error("⚠️ 無法讀取雲端出團目標，請確認網址。")

# 動態抓取最高指揮官
if st.session_state.sheet_url_commanders:
    try:
        df_c = pd.read_csv(st.session_state.sheet_url_commanders, header=None, encoding='utf-8')
        if not df_c.empty:
            raw_list = df_c.iloc[:, 0].dropna().astype(str).tolist()
            COMMANDER_LIST = [x.strip() for x in raw_list if x.strip() and x.strip() != "名字"]
    except Exception as e:
        st.sidebar.error("⚠️ 無法讀取雲端指揮官名單，請確認網址。")

# =====================================================================
# 5. 主介面：安全防空鎖（若雲端為空，顯示警告阻止崩潰）
# =====================================================================
st.markdown("""
    <div class='clan-header'>
        <div class='clan-title'>🏰 狂盟血誓戰盟 - 頂級 AI 戰略行政系統 V32</div>
        <div class='clan-subtitle'>COMMAND CENTER • PURE CLOUD LIVE SYNCHRONIZED VERSION</div>
    </div>
""", unsafe_allow_html=True)

if not VALID_NAMES or not base_targets or not COMMANDER_LIST:
    st.error("🚨 報告老大：系統檢測到目前雲端資料庫抓取為空！請確認左側連動設定中心的 CSV 網址是否填寫正確。")
else:
    st.markdown("<div class='section-tag'>⚔️ 戰報參數設定儀表板 (已與雲端即時同步)</div>", unsafe_allow_html=True)

    # 動態生成出團王組合（自動置頂最熱門的 飛龍+四色+伊佛）
    all_combinations = []
    for r in range(1, len(base_targets) + 1):
        for combo in itertools.combinations(base_targets, r):
            all_combinations.append("+".join(combo))
    if "飛龍+四色+伊佛" in all_combinations:
        all_combinations.remove("飛龍+四色+伊佛")
    all_combinations.insert(0, "飛龍+四色+伊佛")

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
        selected_commander = st.selectbox("👑 戰場最高統帥指揮官:", options=COMMANDER_LIST, index=0 if "齊" in COMMANDER_LIST else 0)

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
    # 6. 操作控制台
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
            button_placeholder = st.empty()
            execute_click = button_placeholder.button("🔥 發動總攻擊！啟動狂盟核心點名認列", key="attack_btn", use_container_width=True)

    with btn_col2:
        if is_uploading:
            pass
        else:
            if st.button("🔄 熔爐重置 / 清理當前戰報準備下一場", key="reset_btn", use_container_width=True):
                st.session_state.uploader_key += 1
                st.rerun()

    # =====================================================================
    # 7. 🎯 狂盟大破大立雲端白名單注入提示詞
    # =====================================================================
    white_list_str = "、".join(VALID_NAMES)
    PROMPT_TEMPLATE = f"""
    你現在是《天堂》遊戲血盟的頂級行政秘書。請對這張圖片左下角的「藍色小隊名單 UI 區塊」進行地毯式掃描。
    必須找出名單中的每一個人，絕對不准有任何遺漏！

    請逐字核對以下【狂盟官方白名單】：
    {white_list_str}

    【👑 特級鐵律：隊長與名單分離】
    1. 隊伍最上面第一行（正前方帶有黃金皇冠圖標）的名字是「隊長」。如果最上面看到的是單字「齊」，請確認他是獨立的一行，他就是隊長！絕對不准漏掉他，也不准把他和下方的隊員合在一起！
    2. 請由上到下，精準輸出小隊中所有符合白名單的名字。每行一個名字。

    【精準輸出格式】：
    不准輸出任何額外廢話，嚴格依據以下格式回傳：
    [LEADER] 隊長名字
    [MEMBER] 隊員名字
    [MEMBER] 隊員名字
    """

    # =====================================================================
    # 8. 核心處理與報告輸出
    # =====================================================================
    if execute_click:
        if not api_key:
            st.error("⚠️ 老大！請先在左側邊欄鎖定您的 狂盟核心 API 金鑰！")
        elif uploaded_files:
            button_placeholder.markdown("""
                <div class='clan-loading-box'>
                    ⚡ 狂盟核心雲端最新資料已就緒 + 熔爐正全馬力運算... 請老大稍候...
                </div>
            """, unsafe_allow_html=True)
            
            time.sleep(0.2)
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            date_str = selected_date.strftime("%Y%m%d")
            raw_text_report = ""
            
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
                        cleaned = line.replace("[LEADER]", "").replace("[MEMBER]", "").replace("(隊長)", "").strip()
                        
                        matched_name = None
                        for v_name in VALID_NAMES:
                            if v_name in cleaned.replace(" ", ""):
                                matched_name = v_name
                                break
                        
                        if matched_name:
                            has_any_data = True
                            excel_row_base = f"{global_excel_idx}\t{date_str}\t{selected_time}\t{selected_target}\t{selected_commander}\t{matched_name}"
                            
                            is_leader = "[LEADER]" in line or "隊長" in line or local_team_idx == 1
                            
                            if is_leader:
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
            
            button_placeholder.button("🔥 發動總攻擊！啟動狂盟核心點名認列", key="attack_btn_done", use_container_width=True)
            
            if has_any_data:
                st.markdown("<br><div class='section-tag'>📋 狂盟直貼 Excel 數據中心 (完美相容 7 大直欄)</div>", unsafe_allow_html=True)
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
