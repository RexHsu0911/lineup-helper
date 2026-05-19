import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import re
import difflib
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置網頁分頁標題與圖示
st.set_page_config(page_title="狂盟血盟後台系統-6核天譴版", page_icon="🏰", layout="wide")

# =====================================================================
# 1. 狂盟尊爵視覺風格 (CSS V45 6核深淵金屬版)
# =====================================================================
st.markdown("""
    <style>
    .main { background-color: #050507; color: #e5e5e7; font-family: 'Microsoft JhengHei', sans-serif; }
    [data-testid="stSidebar"] { background-color: #09090b !important; border-right: 3px solid #d4af37; }
    .clan-header {
        background: linear-gradient(135deg, rgba(220,0,0,0.4) 0%, rgba(8,8,10,0.98) 50%, rgba(212,175,55,0.25) 100%);
        border: 2px solid #d4af37; border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 35px;
        box-shadow: 0 0 35px rgba(255,0,0,0.5), inset 0 0 20px rgba(212,175,55,0.2);
    }
    .clan-title { color: #ff0000; font-weight: 900; font-size: 44px; text-shadow: 3px 3px 6px #000000, 0 0 35px #ff0000, 0 0 10px #ffffff; letter-spacing: 7px; margin: 0; }
    .clan-subtitle { color: #d4af37; font-size: 16px; letter-spacing: 4px; margin-top: 8px; font-weight: bold; }
    .report-box { background: linear-gradient(145deg, #0a0a0d, #111115); border: 2px solid #d4af37; padding: 35px; border-radius: 10px; box-shadow: 0 25px 50px rgba(0,0,0,0.95); }
    .section-tag { color: #ffffff; font-size: 19px; font-weight: bold; background: linear-gradient(90deg, #b30000 0%, rgba(179,0,0,0.1) 70%, transparent 100%); padding: 8px 18px; border-radius: 4px; border-left: 6px solid #ff0000; }
    .leader-orange { color: #ff4500 !important; font-weight: bold !important; padding-left: 20px; font-size: 17px; margin: 4px 0; text-shadow: 1px 1px 2px #000; }
    .member-w { color: #e5e5e7; padding-left: 20px; margin: 4px 0; font-size: 16px; }
    .auto-corrected-yellow { color: #ffcc00 !important; font-weight: bold !important; padding-left: 20px; font-size: 16px; margin: 4px 0; }
    .unconfirmed-red { color: #ff0000 !important; font-weight: bold !important; padding-left: 20px; font-size: 16px; margin: 4px 0; }
    div.stButton > button[key="attack_btn"] {
        background: linear-gradient(180deg, #ff0000 0%, #b30000 50%, #550000 100%) !important; color: #ffffff !important; font-weight: 900 !important; font-size: 26px !important;
        border: 2px solid #ffcc00 !important; box-shadow: 0 0 30px rgba(255,0,0,0.9) !important; height: 75px !important; border-radius: 8px !important; letter-spacing: 5px !important;
    }
    .stProgress > div > div > div > div { background-color: #ff0000 !important; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. 側邊欄配置 - 6核天譴金鑰火炮庫
# =====================================================================
st.sidebar.markdown("<h3 style='color:#d4af37; text-align:center;'>🌋 6核聯防金鑰矩陣</h3>", unsafe_allow_html=True)
# 預填老大剛剛給的6組黃金金鑰
default_keys = "AIzaSyDlNNsba7uaIPQrCvKB2Gv-i5xnOi9jSEw,AIzaSyBovkSnQ3SKQ0Udai2cLjqu0y4gqXvmycI,AIzaSyAKQZO2OcbmNRHjmvxACqOGw20uUaTKjT8,AIzaSyDb5_Do5uOkOi6qh1jNmRhFmZwEAvTXbZE,AIzaSyAzP8B-5PwhW7w3E2gGDJTsI0n4erU9hJI,AIzaSyAzYWwQgC4t58pZtx80wFja42gTcM8Fpc0"
api_input = st.sidebar.text_area("🔑 當前已裝填金鑰庫：", value=default_keys)

API_KEYS_POOL = [k.strip() for k in re.split(r'[;,，\n]', api_input) if k.strip()]

st.sidebar.markdown(f"<p style='color:#00ffcc; font-weight:bold; text-align:center;'>🔥 已成功綁定 {len(API_KEYS_POOL)} 組核動力金鑰</p>", unsafe_allow_html=True)

st.sidebar.markdown("---")
default_url_m = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQTnOiq6sWHfimLY5BTNOSf5pyXHNcymkxYHr2hyN8ChS0qBt3qCcldc3cdqJu7BXzjZccA8dpwIiah/pub?gid=0&single=true&output=csv"
url_m = st.sidebar.text_input("📋 成員白名單 CSV 網址：", value=default_url_m)

# 加載白名單
VALID_NAMES = []
if url_m:
    try:
        df_m = pd.read_csv(url_m.strip(), header=None, skiprows=[0], encoding='utf-8')
        if not df_m.empty: VALID_NAMES = [str(x).strip() for x in df_m.iloc[:, 0].dropna().tolist() if str(x).strip()]
    except: pass

# =====================================================================
# 3. 智慧解構與文字碰撞演算法
# =====================================================================
def parse_filename_data(filename):
    name_clean = re.sub(r'\.(jpg|jpeg|png|PNG|JPG|JPEG)$', '', filename).strip()
    date_out, time_out, target_out, commander_out, team_num_out = "20260518", "0000", "未明", "無", "1"
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
        else: target_parts.append(tk)
    if target_parts: target_out = " ".join(target_parts)
    return date_out, time_out, target_out, commander_out, team_num_out

def is_ai_garbage_text(text):
    """鋼鐵過濾網：精準擊殺AI碎碎念的客套廢話"""
    garbage_keywords = ["好的", "血盟行政", "秘書", "完成精確", "辨識", "截圖中", "出現的所有", "以下是", "遵命", "小隊成員"]
    match_count = sum(1 for kw in garbage_keywords if kw in text)
    if match_count >= 2 or len(text) > 15: # 正常ID很少超過15個字且帶有客套話
        return True
    return False

def smart_match_name(cleaned_name, white_list):
    hard_rules = {"什麼漢字": "什麼漾子", "什麼樣區": "什麼漾子"}
    if cleaned_name in hard_rules: return hard_rules[cleaned_name], 'FIXED', f" (常用錯字特赦 ➔ {hard_rules[cleaned_name]})"
    alt_cleaned = cleaned_name.replace("气", "氣").replace("1", "一")
    for v_name in white_list:
        if v_name.replace(" ", "") in [cleaned_name, alt_cleaned]: return v_name, 'EXACT', ""
    matches = difflib.get_close_matches(cleaned_name, white_list, n=3, cutoff=0.6)
    if len(matches) == 1: return matches[0], 'FIXED', f" (AI智慧修正自: {cleaned_name})"
    elif len(matches) > 1: return cleaned_name, 'AMBIGUOUS', f" <span style='color:#8c8c9e; font-size:13px;'>[🚨 白名單相近字疑犯: {'、'.join(matches)}]</span>"
    return cleaned_name, 'AMBIGUOUS', ""

# =====================================================================
# 4. 🚀 6核異步單圖處理器
# =====================================================================
def process_single_image(task_args):
    file_bytes, filename, api_key_to_use = task_args
    try:
        genai.configure(api_key=api_key_to_use)
        model = genai.GenerativeModel('gemini-2.5-flash')
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        
        prompt = (
            "你現在是血盟行政秘書。請精確辨識這張小隊截圖裡出現的所有人，絕對不准漏掉！\n"
            "第一行（最上面前方有黃冠圖標）的是隊長！請嚴格遵循以下格式回傳：\n"
            "[LEADER] 隊長名字\n"
            "[MEMBER] 隊員名字\n"
            "[MEMBER] 隊員名字\n"
            "注意：不要說任何客套話，直接輸出名單格式即可。"
        )
        response = model.generate_content([prompt, img])
        img.close()
        return {"filename": filename, "status": "SUCCESS", "text": response.text}
    except Exception as e:
        return {"filename": filename, "status": "FAILED", "text": str(e)}

# =====================================================================
# 5. 主介面
# =====================================================================
st.markdown("<div class='clan-header'><div class='clan-title'>🏰 狂盟血誓戰盟 - 6核天譴暴風控制台 V45</div><div class='clan-subtitle'>6-CORE PARALLEL ULTRA-SPEED PROCESSING SYSTEM</div></div>", unsafe_allow_html=True)

if not VALID_NAMES:
    st.error("🚨 報告老大：系統檢測到目前雲端成員資料庫抓取為空！請確認 CSV 網址。")
else:
    st.markdown("<div class='section-tag'>📸 6核飽和火力 - 百圖影像大熔爐 (極速狂飆版)</div>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("請直接全選丟入今天的所有截圖（6組金鑰全開，速度提升600%）：", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

    if uploaded_files:
        st.success(f"📈 報告老大：成功載入 {len(uploaded_files)} 張戰場影像！6核齊發準備完畢。")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔥 啟動6核深淵熔爐！百圖會戰一鍵地毯式點名", key="attack_btn", use_container_width=True):
        if not API_KEYS_POOL:
            st.error("⚠️ 老大！請先在左側邊欄確認金鑰是否正確裝填！")
        elif not uploaded_files:
            st.warning("⚠️ 老大，您還沒有丟任何戰場截圖進來啊！")
        else:
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            # 裝填任務參數
            tasks_args = []
            num_keys = len(API_KEYS_POOL)
            for idx, f in enumerate(uploaded_files):
                f.seek(0)
                tasks_args.append((f.read(), f.name, API_KEYS_POOL[idx % num_keys]))
            
            results = []
            total_tasks = len(tasks_args)
            
            # 6組金鑰全開，並發線程數直接拉高到 8-10，速度拉滿且絕不卡死
            with ThreadPoolExecutor(max_workers=8) as executor:
                future_to_filename = {executor.submit(process_single_image, arg): arg[1] for arg in tasks_args}
                
                completed_count = 0
                for future in as_completed(future_to_filename):
                    completed_count += 1
                    results.append(future.result())
                    
                    # 動態刷新進度
                    pct = completed_count / total_tasks
                    progress_bar.progress(pct)
                    status_text.markdown(f"<b style='color:#ffcc00;'>⚡ 6核火炮瘋狂齊射中：已消滅 {completed_count} / {total_tasks} 張截圖... 戰場進度 {int(pct*100)}%</b>", unsafe_allow_html=True)
            
            status_text.markdown("<b style='color:#00ffcc;'>✅ 報告老大：100張大會戰截圖已全部擊穿！正在過濾AI廢話並生成最終大總表...</b>", unsafe_allow_html=True)
            
            # =====================================================================
            # 6. 鋼鐵過濾與統合生成最終大總表
            # =====================================================================
            report_html = "<div class='report-box'><div class='section-tag' style='background:none; border:none; padding:0; color:#ff0000; font-size:20px;'>🦅 狂盟 6 核天譴會戰 - 最終純淨大總表</div>"
            
            global_excel_idx = 1
            raw_text_report = ""
            REGISTERED_NAMES_POOL = set()
            
            results_sorted = sorted(results, key=lambda x: x["filename"])
            
            for res in results_sorted:
                filename = res["filename"]
                d_row, t_row, tg_row, cmd_row, tm_row = parse_filename_data(filename)
                
                report_html += f"""
                <div style='margin-top:12px; background-color:#121216; padding:8px; border-left:4px solid #ffcc00;'>
                    <span style='color:#d4af37; font-weight:bold;'>📸 分隊 {tm_row}</span> <span style='color:#888; font-size:12px;'>({filename})</span> | 
                    <span style='color:#aaa; font-size:13px;'>{d_row} | {t_row} | 目標: {tg_row} | 統帥: {cmd_row}</span>
                </div><br>
                """
                
                if res["status"] == "FAILED":
                    report_html += f"<div class='unconfirmed-red'>❌ 該圖片解析失敗：{res['text']}</div>"
                    continue
                    
                local_idx = 1
                has_leader_assigned = False # 確保一隊只有一個隊長的安全鎖
                lines = res["text"].strip().split('\n')
                
                for line in lines:
                    cleaned = line.replace("[LEADER]", "").replace("[MEMBER]", "").replace(" ", "").strip()
                    if not cleaned or "---" in cleaned: continue
                    
                    # 鋼鐵過濾網：直接拍死 AI 的客套碎碎念
                    if is_ai_garbage_text(cleaned): continue
                    
                    final_name, match_status, hint_msg = smart_match_name(cleaned, VALID_NAMES)
                    
                    # 判斷是否為隊長（且該隊目前還沒有合法隊長）
                    is_leader = ("[LEADER]" in line or local_idx == 1) and not has_leader_assigned
                    if is_leader:
                        has_leader_assigned = True
                        
                    position_str = "隊長" if is_leader else ""
                    leader_suffix = " (隊長)" if is_leader else ""
                    
                    unique_key = f"{d_row}_{t_row}_{final_name}"
                    is_duplicate = unique_key in REGISTERED_NAMES_POOL
                    REGISTERED_NAMES_POOL.add(unique_key)
                    
                    if is_duplicate:
                        display_name = f"{final_name}(重複登記)"
                        raw_text_report += f"{global_excel_idx}\t{d_row}\t{t_row}\t{tg_row}\t{cmd_row}\t{display_name}\t{position_str}\n"
                        report_html += f"<div class='unconfirmed-red'>{local_idx}. ⚠️ {final_name} (重複登記){leader_suffix}</div>"
                    elif match_status == 'EXACT':
                        raw_text_report += f"{global_excel_idx}\t{d_row}\t{t_row}\t{tg_row}\t{cmd_row}\t{final_name}\t{position_str}\n"
                        if is_leader: report_html += f"<div class='leader-orange'>{local_idx}. 🎖️ {final_name}{leader_suffix}</div>"
                        else: report_html += f"<div class='member-w'>{local_idx}. {final_name}</div>"
                    elif match_status == 'FIXED':
                        raw_text_report += f"{global_excel_idx}\t{d_row}\t{t_row}\t{tg_row}\t{cmd_row}\t{final_name}\t{position_str}\n"
                        report_html += f"<div class='auto-corrected-yellow'>{local_idx}. 🌟 {final_name}{leader_suffix}<span style='font-size:12px; color:#aaa;'>{hint_msg}</span></div>"
                    else:
                        display_name = f"{final_name}(待確認/更新)"
                        raw_text_report += f"{global_excel_idx}\t{d_row}\t{t_row}\t{tg_row}\t{cmd_row}\t{display_name}\t{position_str}\n"
                        report_html += f"<div class='unconfirmed-red'>{local_idx}. ⚠️ {final_name} (待確認/更新){leader_suffix}{hint_msg}</div>"
                    
                    local_idx += 1
                    global_excel_idx += 1
                    
            report_html += "</div>"
            st.markdown(report_html, unsafe_allow_html=True)
            
            if raw_text_report:
                st.markdown("<br><div class='section-tag'>📋 狂盟直貼 Excel 數據中心 (6核統合純淨數據)</div>", unsafe_allow_html=True)
                st.text_area("", value=raw_text_report.strip(), height=300, key="copy_target", label_visibility="collapsed")
                
                escaped_text = raw_text_report.strip().replace("`", "\\`").replace("'", "\\'")
                js_button_html = f"""
                <div style="text-align: center; width: 100%;">
                    <button onclick="navigator.clipboard.writeText(`{escaped_text}`).then(() => alert('📋 報告老大：V45 6核深淵統合數據已完美複製！AI廢話已全部清除！'));" 
                    style="width: 100%; background: linear-gradient(180deg, #cc0000 0%, #880000 100%); color: white; border: 2px solid #d4af37; padding: 18px; font-size: 18px; font-weight: bold; border-radius: 6px; cursor: pointer; box-shadow: 0 6px 15px rgba(255,0,0,0.4); letter-spacing:2px;">
                        🦅 一鍵秒複製 6 核暴風純淨總表 🦅
                    </button>
                </div>
                """
                st.components.v1.html(js_button_html, height=80)
