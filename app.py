import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import datetime
import itertools
import time
import re
import difflib  # 引入智慧文字比對核心
import pandas as pd

# 配置網頁分頁標題與圖示
st.set_page_config(page_title="狂盟血盟後台系統", page_icon="🏰", layout="wide")

# =====================================================================
# 1. 狂盟尊爵：天堂經典血誓不朽視覺風格 (CSS V42 智慧容錯版)
# =====================================================================
st.markdown("""
    <style>
    .main { 
        background-color: #060608; 
        color: #e5e5e7; 
        font-family: 'Microsoft JhengHei', 'Segoe UI', sans-serif; 
    }
    [data-testid="stSidebar"] {
        background-color: #0b0b0d !important;
        border-right: 3px solid #d4af37;
    }
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
    .report-box { 
        background: linear-gradient(145deg, #0f0f12, #15151a);
        border: 2px solid #d4af37; 
        padding: 35px; 
        border-radius: 10px; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.9), 0 0 20px rgba(212,175,55,0.15);
    }
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
    .img-title { 
        color: #ffcc00; 
        font-weight: bold; 
        font-size: 17px; 
        margin-top: 28px; 
        display: block;
        border-bottom: 2px solid #443615;
        padding-bottom: 6px;
    }
    .filename-pill {
        background-color: #1a1a24;
        color: #00ffcc;
        border: 1px solid #00aa88;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 14px;
    }
    .leader-orange { color: #ff4500 !important; font-weight: bold !important; padding-left: 20px; font-size: 17px; margin: 8px 0; text-shadow: 1px 1px 4px #000; }
    .member-w { color: #e5e5e7; padding-left: 20px; margin: 6px 0; font-size: 16px; }
    .auto-corrected-yellow { color: #ffcc00 !important; font-weight: bold !important; padding-left: 20px; font-size: 16px; margin: 6px 0; text-shadow: 0 0 5px rgba(255,204,0,0.4); }
    .unconfirmed-red { color: #ff0000 !important; font-weight: bold !important; padding-left: 20px; font-size: 16px; margin: 6px 0; text-shadow: 0 0 10px rgba(255,0,0,0.5); }
    .suspect-hint { color: #8c8c9e !important; font-size: 13px !important; font-weight: normal !important; font-style: italic; }
    label { color: #d4af37 !important; font-weight: bold !important; font-size: 16px !important; letter-spacing: 1px; text-shadow: 1px 1px 2px #000; }
    div[data-testid="stFileUploader"] { background-color: #0b0b0d; border: 2px dashed #b30000 !important; border-radius: 10px; padding: 15px; }
    div.stButton > button[key="attack_btn"] {
        background: linear-gradient(180deg, #ff0000 0%, #aa0000 50%, #660000 100%) !important; color: #ffffff !important; font-weight: 900 !important; font-size: 22px !important;
        border: 2px solid #ffcc00 !important; box-shadow: 0 0 20px rgba(255,0,0,0.7) !important; text-shadow: 2px 2px 5px #000000, 0 0 10px #ff0000 !important;
        letter-spacing: 3px !important; height: 65px !important; border-radius: 8px !important;
    }
    div.stButton > button[key="attack_btn"]:hover { background: linear-gradient(180deg, #ff3333 0%, #cc0000 50%, #880000 100%) !important; box-shadow: 0 0 35px rgba(255,0,0,1) !important; }
    div.stButton > button[key="reset_btn"] { background: linear-gradient(180deg, #333338 0%, #1c1c1f 50%, #0d0d0f 100%) !important; color: #d4af37 !important; font-weight: 900 !important; font-size: 18px !important; border: 2px solid #554518 !important; height: 65px !important; border-radius: 8px !important; }
    .clan-loading-wrapper { display: flex; justify-content: center; align-items: center; width: 100%; }
    .clan-loading-box {
        width: 100%; max-width: 600px; background: linear-gradient(135deg, #150505 0%, #080202 100%); border: 2px dashed #ff0000; padding: 15px; text-align: center; border-radius: 8px;
        box-shadow: 0 0 25px rgba(255,0,0,0.6); color: #ff3333; font-size: 18px; font-weight: bold; animation: pulseBlinker 2s linear infinite; height: 55px; line-height: 22px;
    }
    @keyframes pulseBlinker { 0% { opacity: 0.7; } 50% { opacity: 1.0; color: #ffbcbc; } 100% { opacity: 0.7; } }
    .clan-table-container { margin-top: 5px; margin-bottom: 5px; border: 1px solid #d4af37; border-radius: 4px; overflow: hidden; }
    .clan-table { width: 100%; border-collapse: collapse; background-color: #0c0c0e; text-align: center; }
    .clan-table th { background: linear-gradient(180deg, #1a1a1e 0%, #0d0d10 100%); color: #d4af37; font-weight: bold; font-size: 14px; padding: 8px; border-bottom: 1px solid #33270c; border-right: 1px solid #221a08; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. 🛡️ 鐵血防禦：安全鎖定錨點與白名單同步
# =====================================================================
if 'saved_api_key' not in st.session_state: st.session_state['saved_api_key'] = ""
if 'uploader_key' not in st.session_state: st.session_state['uploader_key'] = 0

default_url_m = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQTnOiq6sWHfimLY5BTNOSf5pyXHNcymkxYHr2hyN8ChS0qBt3qCcldc3cdqJu7BXzjZccA8dpwIiah/pub?gid=0&single=true&output=csv"
if 'sheet_url_members' not in st.session_state: st.session_state['sheet_url_members'] = default_url_m

# 加載成員白名單
VALID_NAMES = []
if st.session_state['sheet_url_members']:
    try:
        df_m = pd.read_csv(st.session_state['sheet_url_members'], header=None, skiprows=[0], encoding='utf-8')
        if not df_m.empty: VALID_NAMES = [str(x).strip() for x in df_m.iloc[:, 0].dropna().tolist() if str(x).strip()]
    except: pass

# =====================================================================
# 3. 側邊欄配置
# =====================================================================
st.sidebar.markdown("<h3 style='color:#d4af37; text-align:center;'>🏰 神殿權限配置</h3>", unsafe_allow_html=True)
api_key = st.sidebar.text_input("🔑 核心 API 認證金鑰：", value=st.session_state['saved_api_key'], type="password")
if api_key: st.session_state['saved_api_key'] = api_key

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#00ffcc; text-align:center;'>🌐 雲端連動設定中心</h3>", unsafe_allow_html=True)
url_m = st.sidebar.text_input("📋 成員白名單 CSV 網址：", value=st.session_state['sheet_url_members'])
if url_m: st.session_state['sheet_url_members'] = url_m.strip()

# =====================================================================
# 4. 智慧容錯與檔名解構核心工具組
# =====================================================================
def parse_filename_data(filename):
    name_clean = re.sub(r'\.(jpg|jpeg|png|PNG|JPG|JPEG)$', '', filename).strip()
    date_out, time_out, target_out, commander_out, team_num_out = "20260517", "0000", "未明", "無", "1"
    
    if '-' in name_clean:
        parts_dash = name_clean.split('-')
        team_num_out = parts_dash[-1].strip()
        name_clean = "-".join(parts_dash[:-1]).strip()
        
    tokens = [t.strip() for t in name_clean.split(' ') if t.strip()]
    if len(tokens) >= 1:
        raw_date = tokens[0]
        date_out = f"2026{raw_date}" if len(raw_date) == 4 else raw_date
    if len(tokens) >= 2: time_out = tokens[1]
    
    remains = tokens[2:] if len(tokens) > 2 else []
    target_parts = []
    for tk in remains:
        if "指揮官" in tk:
            cmd_clean = tk.replace("指揮官", "").replace(":", "").replace("-", "").strip()
            if cmd_clean: commander_out = cmd_clean
        else:
            target_parts.append(tk)
    if target_parts: target_out = " ".join(target_parts)
    return date_out, time_out, target_out, commander_out, team_num_out

def smart_match_name(cleaned_name, white_list):
    """
    ⚔️ 智慧容錯大腦 V42
    傳回值：(最終認列名字, 狀態代碼, 提示文字)
    狀態代碼: 'EXACT' (完全相符), 'FIXED' (核心自動修正), 'AMBIGUOUS' (多個長很像/找不到)
    """
    # 1. 核心大特赦：強制優先修正老大指定的終極大錯字
    hard_rules = {
        "什麼漢字": "什麼漾子",
        "什麼樣區": "什麼漾子"
    }
    if cleaned_name in hard_rules:
        return hard_rules[cleaned_name], 'FIXED', f" (常用錯字特赦 ➔ {hard_rules[cleaned_name]})"

    # 進行一些基本的簡繁、基本通訊錯字預處理
    alt_cleaned = cleaned_name.replace("气", "氣").replace("1", "一")
    
    # 2. 第一層：地毯式完全比對
    for v_name in white_list:
        v_clean = v_name.replace(" ", "")
        if v_clean == cleaned_name or v_clean == alt_cleaned:
            return v_name, 'EXACT', ""

    # 3. 第二層：智慧模糊比對（尋找高度相似字）
    # get_close_matches 會計算相似度，cutoff=0.6 代表要 60% 以上像
    matches = difflib.get_close_matches(cleaned_name, white_list, n=3, cutoff=0.6)
    if not matches:
        matches = difflib.get_close_matches(alt_cleaned, white_list, n=3, cutoff=0.6)

    if len(matches) == 1:
        # 唯一只有一個人長得很像，系統自動判定特赦修正
        return matches[0], 'FIXED', f" (AI智慧修正自: {cleaned_name})"
    elif len(matches) > 1:
        # 超過一個以上的人長得很像（例如 狂盟帥哥、狂盟帥弟 分不出來），絕對不瞎猜，交給老大裁決
        suspects = "、".join(matches)
        return cleaned_name, 'AMBIGUOUS', f" <span class='suspect-hint'>[🚨 白名單相近字疑犯: {suspects}]</span>"
    
    # 完全找不到任何長得像的
    return cleaned_name, 'AMBIGUOUS', ""

# =====================================================================
# 5. 主介面儀表板
# =====================================================================
st.markdown("""
    <div class='clan-header'>
        <div class='clan-title'>🏰 狂盟血誓戰盟 - 頂級 AI 戰略行政系統 V42</div>
        <div class='clan-subtitle'>COMMAND CENTER • INTELLIGENT FUZZY MATCHING & DISAMBIGUATION VERSION</div>
    </div>
""", unsafe_allow_html=True)

if not VALID_NAMES:
    st.error("🚨 報告老大：系統檢測到目前雲端成員資料庫抓取為空！請確認左側 CSV 網址。")
else:
    st.markdown("<div class='section-tag'>📸 戰場軍情影像熔爐 (💡 V42 智慧相近字防錯糾錯版)</div>", unsafe_allow_html=True)
    
    current_key_val = st.session_state.get('uploader_key', 0)
    uploaded_files = st.file_uploader(
        "請直接將已改好檔名的小隊截圖拖曳至此：", 
        accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key=f"uploader_{current_key_val}"
    )

    if uploaded_files:
        st.markdown("<b style='color:#3a86c8;'>🖼️ 戰場核心影像載入與檔名解析預覽：</b>", unsafe_allow_html=True)
        cols = st.columns(min(len(uploaded_files), 4))
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 4]:
                file.seek(0)
                d, t, tg, cmd, tm = parse_filename_data(file.name)
                img_preview = Image.open(io.BytesIO(file.read()))
                st.image(img_preview, use_container_width=True)
                st.markdown(f"""
                <div style='background-color:#111; padding:8px; border:1px solid #33270c; border-radius:5px; font-size:13px; line-height:1.5;'>
                    <b style='color:#d4af37;'>📄 檔名:</b> <span class='filename-pill'>{file.name}</span><br>
                    <b style='color:#00ffcc;'>📅 解析:</b> {d} | {t}<br>
                    <b style='color:#ff00ff;'>🎯 目標:</b> {tg}<br>
                    <b style='color:#ff4500;'>👑 統帥:</b> {cmd} | <b style='color:#ffcc00;'>分隊:</b> {tm}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        button_placeholder = st.empty()
        execute_click = button_placeholder.button("🔥 發動總攻擊！啟動狂盟核心點名認列", key="attack_btn", use_container_width=True)
    with btn_col2:
        if st.button("🔄 熔爐重置 / 清理當前戰報準備下一場", key="reset_btn", use_container_width=True):
            st.session_state['uploader_key'] = st.session_state.get('uploader_key', 0) + 1
            st.rerun()

    # =====================================================================
    # 6. 核心處理大腦：多圖拼接、檔名解析與智慧文字碰撞
    # =====================================================================
    if execute_click:
        if not api_key:
            st.error("⚠️ 老大！請先在左側邊欄鎖定您的 狂盟核心 API 金鑰！")
        elif uploaded_files:
            button_placeholder.markdown("<div class='clan-loading-wrapper'><div class='clan-loading-box'>⚡ V42 智慧容錯大熔爐啟動：正在重組圖片並注入 AI 防錯引擎...</div></div>", unsafe_allow_html=True)
            
            pil_images = []
            meta_data_map = {}
            for idx, file in enumerate(uploaded_files, start=1):
                file.seek(0)
                img = Image.open(io.BytesIO(file.read())).convert("RGB")
                pil_images.append(img)
                d, t, tg, cmd, tm = parse_filename_data(file.name)
                meta_data_map[idx] = {"date": d, "time": t, "target": tg, "commander": cmd, "team_num": tm, "filename": file.name}
            
            max_w = max(img.width for img in pil_images)
            spacer_h = 40
            total_h = sum(img.height for img in pil_images) + (len(pil_images) - 1) * spacer_h
            fused_image = Image.new("RGB", (max_w, total_h), (0, 0, 0))
            current_y = 0
            
            image_seperator_instructions = ""
            for idx, img in enumerate(pil_images, start=1):
                fused_image.paste(img, (0, current_y))
                image_seperator_instructions += f"第 {idx} 張圖片的開合標記是 [IMAGE_START_{idx}]，對應分隊號為 {meta_data_map[idx]['team_num']}。\n"
                current_y += img.height + spacer_h
            
            REGISTERED_NAMES_POOL = set()
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            white_list_str = "、".join(VALID_NAMES)
            
            PROMPT_TEMPLATE = (
                "你現在是《天堂》遊戲血盟的頂級行政秘書。\n"
                "我上傳了一張由多張血盟小隊截圖「垂直拼接而成」的超大長圖。請由上到下進行地毯式掃描，絕對不准漏掉任何一個人的名字！\n\n"
                f"【圖片分界對照指示】：\n{image_seperator_instructions}\n"
                f"請逐字核對以下【狂盟官方白名單】數據：\n{white_list_str}\n\n"
                "【🔥 頂級特級鐵律】\n"
                "1. 請依據拼接順序，精確辨識出每一張原圖裡出現的人。在輸出時，必須先打出該圖的標記如 `--- IMAGE 1 ---`，再輸出名單。\n"
                "2. 每張小隊圖中最上面第一行（前方有黃金皇冠圖標）的是該隊「隊長」！必須獨立認列，絕對不准漏掉！\n"
                "3. 只要出現在小隊欄位中的名字，不論是否在白名單內，都必須完整輸出！如果白名單找不到，就直接原字原樣輸出！\n\n"
                "【精準輸出格式】：\n"
                "--- IMAGE 1 ---\n"
                "[LEADER] 隊長名字\n"
                "[MEMBER] 隊員名字"
            )
            
            try:
                response = model.generate_content([PROMPT_TEMPLATE, fused_image])
                ai_output = response.text
                
                report_html = f"<div class='report-box'><div class='section-tag' style='background:none; border:none; padding:0; color:#ff0000; font-size:20px;'>🦅 狂盟點名大會師 - 成果報告庫 (V42 智慧容錯解構版)</div>"
                
                global_excel_idx = 1
                has_any_data = False
                raw_text_report = ""
                current_img_idx = 0
                local_team_idx = 1
                
                lines = ai_output.strip().split('\n')
                for line in lines:
                    line_upper = line.upper()
                    if "--- IMAGE" in line_upper or "IMAGE_" in line_upper:
                        import re
                        match = re.search(r'\d+', line)
                        if match:
                            current_img_idx = int(match.group())
                            local_team_idx = 1
                            meta = meta_data_map.get(current_img_idx, {"date":"未知", "time":"未知", "target":"未知", "commander":"無", "team_num":str(current_img_idx), "filename":"未知"})
                            report_html += f"""
                            <div style='margin-top:20px; background-color:#121216; padding:12px; border-left:4px solid #ffcc00; border-radius:4px;'>
                                <span style='color:#ffcc00; font-weight:bold; font-size:16px;'>📸 戰術分隊 {meta['team_num']}</span> <span style='color:#888; font-size:13px;'>({meta['filename']})</span><br>
                                <span style='color:#aaa; font-size:14px;'>戰報連動 ➔ 日期: <b style='color:#fff;'>{meta['date']}</b> | 時間: <b style='color:#fff;'>{meta['time']}</b> | 目標: <b style='color:#00ffcc;'>{meta['target']}</b> | 指揮官: <b style='color:#ff3333;'>{meta['commander']}</b></span>
                            </div><br>
                            """
                        continue
                    
                    if not current_img_idx: 
                        current_img_idx = 1
                        meta = meta_data_map.get(current_img_idx, {"date":"未知", "time":"未知", "target":"未知", "commander":"無", "team_num":"1", "filename":"未知"})
                        report_html += f"<div style='margin-top:20px; background-color:#121216; padding:12px; border-left:4px solid #ffcc00;'><span style='color:#ffcc00; font-weight:bold;'>📸 戰術分隊 1</span></div><br>"
                        
                    cleaned = line.replace("[LEADER]", "").replace("[MEMBER]", "").replace("(隊長)", "").replace(" ", "").strip()
                    if not cleaned or "---" in cleaned: continue
                        
                    current_meta = meta_data_map.get(current_img_idx, {"date":"20260517", "time":"0000", "target":"未明", "commander":"無", "team_num":"1"})
                    d_row, t_row, tg_row, cmd_row = current_meta["date"], current_meta["time"], current_meta["target"], current_meta["commander"]
                    
                    # 🚀 呼叫 V42 智慧文字碰撞核心
                    final_name, match_status, hint_msg = smart_match_name(cleaned, VALID_NAMES)
                    
                    is_leader = "[LEADER]" in line or "隊長" in line or local_team_idx == 1
                    position_str = "隊長" if is_leader else ""
                    has_any_data = True
                    
                    # 跨時空防重檢查
                    unique_key = f"{d_row}_{t_row}_{final_name}"
                    is_duplicate = unique_key in REGISTERED_NAMES_POOL
                    REGISTERED_NAMES_POOL.add(unique_key)
                    
                    leader_suffix = " (隊長)" if is_leader else ""
                    
                    if is_duplicate:
                        display_name = f"{final_name}(重複登記)"
                        raw_text_report += f"{global_excel_idx}\t{d_row}\t{t_row}\t{tg_row}\t{cmd_row}\t{display_name}\t{position_str}\n"
                        report_html += f"<div class='unconfirmed-red'>{local_team_idx}. ⚠️ {final_name} <span style='color:#ff0000; font-weight:bold;'>(重複登記)</span>{leader_suffix}</div>"
                    elif match_status == 'EXACT':
                        raw_text_report += f"{global_excel_idx}\t{d_row}\t{t_row}\t{tg_row}\t{cmd_row}\t{final_name}\t{position_str}\n"
                        if is_leader: report_html += f"<div class='leader-orange'>{local_team_idx}. 🎖️ {final_name}{leader_suffix}</div>"
                        else: report_html += f"<div class='member-w'>{local_team_idx}. {final_name}</div>"
                    elif match_status == 'FIXED':
                        # 自動修正成功的案例 (亮黃色提示行政人員)
                        raw_text_report += f"{global_excel_idx}\t{d_row}\t{t_row}\t{tg_row}\t{cmd_row}\t{final_name}\t{position_str}\n"
                        report_html += f"<div class='auto-corrected-yellow'>{local_team_idx}. 🌟 {final_name}{leader_suffix}<span style='font-size:12px; font-weight:normal; color:#aaa;'>{hint_msg}</span></div>"
                    else:
                        # 處於模糊狀態或找不到人 (噴紅字並附帶嫌疑犯名單)
                        display_name = f"{final_name}(待確認/更新)"
                        raw_text_report += f"{global_excel_idx}\t{d_row}\t{t_row}\t{tg_row}\t{cmd_row}\t{display_name}\t{position_str}\n"
                        report_html += f"<div class='unconfirmed-red'>{local_team_idx}. ⚠️ {final_name} <span style='color:#ff0000; font-weight:bold;'>(待確認/更新)</span>{leader_suffix}{hint_msg}</div>"
                        
                    local_team_idx += 1
                    global_excel_idx += 1
                    
                report_html += "</div>"
                st.markdown(report_html, unsafe_allow_html=True)
                button_placeholder.button("🔥 發動總攻擊！啟動狂盟核心點名認列", key="attack_btn_done", use_container_width=True)
                
                if has_any_data:
                    st.markdown("<br><div class='section-tag'>📋 狂盟直貼 Excel 數據中心 (完美相容 7 大直欄)</div>", unsafe_allow_html=True)
                    st.markdown("<div class='clan-table-container'><table class='clan-table'><thead><tr><th>序號</th><th>日期</th><th>時間</th><th>出團目標</th><th>指揮官</th><th>成員名單</th><th>職位</th></tr></thead></table></div>", unsafe_allow_html=True)
                    st.text_area("", value=raw_text_report.strip(), height=250, key="copy_target", label_visibility="collapsed")
                    
                    escaped_text = raw_text_report.strip().replace("`", "\\`").replace("'", "\\'")
                    js_button_html = f"""
                    <div style="text-align: center; width: 100%;">
                        <button onclick="navigator.clipboard.writeText(`{escaped_text}`).then(() => alert('📋 報告老大：V42 智慧容錯數據已完美複製！'));" 
                        style="width: 100%; background: linear-gradient(180deg, #cc0000 0%, #880000 100%); color: white; border: 2px solid #d4af37; padding: 18px; font-size: 18px; font-weight: bold; border-radius: 6px; cursor: pointer; box-shadow: 0 6px 15px rgba(255,0,0,0.4); letter-spacing:2px;">
                            🦅 一鍵秒複製 7 大欄位狂盟核心數據 🦅
                        </button>
                    </div>
                    """
                    st.components.v1.html(js_button_html, height=80)
                
            except Exception as ex:
                st.error(f"❌ 大熔爐認列失敗，請重試。錯誤原因: {ex}")
