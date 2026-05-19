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
st.set_page_config(page_title="狂盟血盟後台系統-終極體", page_icon="🏰", layout="wide")

# =====================================================================
# 1. 狂盟尊爵視覺風格 (CSS V44 鋼鐵重工業版)
# =====================================================================
st.markdown("""
    <style>
    .main { background-color: #060608; color: #e5e5e7; font-family: 'Microsoft JhengHei', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0b0b0d !important; border-right: 3px solid #d4af37; }
    .clan-header {
        background: linear-gradient(135deg, rgba(200,0,0,0.35) 0%, rgba(10,10,12,0.95) 50%, rgba(212,175,55,0.2) 100%);
        border: 2px solid #d4af37; border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 35px;
        box-shadow: 0 0 30px rgba(255,0,0,0.4), inset 0 0 20px rgba(212,175,55,0.15);
    }
    .clan-title { color: #ff0000; font-weight: 900; font-size: 42px; text-shadow: 3px 3px 6px #000000, 0 0 30px #ff0000, 0 0 10px #ffffff; letter-spacing: 6px; margin: 0; }
    .clan-subtitle { color: #d4af37; font-size: 16px; letter-spacing: 3px; margin-top: 8px; font-weight: bold; }
    .report-box { background: linear-gradient(145deg, #0d0d10, #131317); border: 2px solid #d4af37; padding: 35px; border-radius: 10px; box-shadow: 0 20px 40px rgba(0,0,0,0.9); }
    .section-tag { color: #ffffff; font-size: 19px; font-weight: bold; background: linear-gradient(90deg, #b30000 0%, rgba(179,0,0,0.1) 70%, transparent 100%); padding: 8px 18px; border-radius: 4px; border-left: 6px solid #ff0000; }
    .filename-pill { background-color: #1a1a24; color: #00ffcc; border: 1px solid #00aa88; padding: 2px 8px; border-radius: 4px; font-family: monospace; }
    .leader-orange { color: #ff4500 !important; font-weight: bold !important; padding-left: 20px; font-size: 17px; margin: 4px 0; text-shadow: 1px 1px 2px #000; }
    .member-w { color: #e5e5e7; padding-left: 20px; margin: 4px 0; font-size: 16px; }
    .auto-corrected-yellow { color: #ffcc00 !important; font-weight: bold !important; padding-left: 20px; font-size: 16px; margin: 4px 0; }
    .unconfirmed-red { color: #ff0000 !important; font-weight: bold !important; padding-left: 20px; font-size: 16px; margin: 4px 0; text-shadow: 0 0 5px rgba(255,0,0,0.3); }
    .suspect-hint { color: #8c8c9e !important; font-size: 13px !important; font-weight: normal !important; font-style: italic; }
    div.stButton > button[key="attack_btn"] {
        background: linear-gradient(180deg, #ff0000 0%, #aa0000 50%, #660000 100%) !important; color: #ffffff !important; font-weight: 900 !important; font-size: 24px !important;
        border: 2px solid #ffcc00 !important; box-shadow: 0 0 25px rgba(255,0,0,0.8) !important; height: 70px !important; border-radius: 8px !important; letter-spacing: 4px !important;
    }
    .stProgress > div > div > div > div { background-color: #ff0000 !important; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. 側邊欄配置 - 金鑰聯防盾牌
# =====================================================================
st.sidebar.markdown("<h3 style='color:#d4af37; text-align:center;'>🏰 100圖聯防金鑰庫</h3>", unsafe_allow_html=True)
api_input = st.sidebar.text_area("🔑 輸入金鑰（處理100張圖強烈建議放 3~5 組金鑰，用逗號或換行隔開）：", value="")

API_KEYS_POOL = [k.strip() for k in re.split(r'[;,，\n]', api_input) if k.strip()]

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
        else: target_parts.append(tk)
    if target_parts: target_out = " ".join(target_parts)
    return date_out, time_out, target_out, commander_out, team_num_out

def smart_match_name(cleaned_name, white_list):
    hard_rules = {"什麼漢字": "什麼漾子", "什麼樣區": "什麼漾子"}
    if cleaned_name in hard_rules: return hard_rules[cleaned_name], 'FIXED', f" (常用錯字特赦 ➔ {hard_rules[cleaned_name]})"
    alt_cleaned = cleaned_name.replace("气", "氣").replace("1", "一")
    for v_name in white_list:
        if v_name.replace(" ", "") in [cleaned_name, alt_cleaned]: return v_name, 'EXACT', ""
    matches = difflib.get_close_matches(cleaned_name, white_list, n=3, cutoff=0.6)
    if len(matches) == 1: return matches[0], 'FIXED', f" (AI智慧修正自: {cleaned_name})"
    elif len(matches) > 1: return cleaned_name, 'AMBIGUOUS', f" <span class='suspect-hint'>[🚨 白名單相近字疑犯: {'、'.join(matches)}]</span>"
    return cleaned_name, 'AMBIGUOUS', ""

# =====================================================================
# 4. 🚀 輕量化單圖處理器（動態控速流）
# =====================================================================
def process_single_image(task_args):
    """
    輕量化單圖處理，加入延遲控速防機制，防止百圖瞬間擊穿 Google 限制
    """
    file_bytes, filename, api_key_to_use, delay = task_args
    if delay > 0:
        time.sleep(delay) # 智慧分流發送，避免爆發連線
        
    try:
        genai.configure(api_key=api_key_to_use)
        model = genai.GenerativeModel('gemini-2.5-flash')
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        
        prompt = (
            "你現在是血盟行政秘書。請精確辨識這張小隊截圖裡出現的所有人，絕對不准漏掉！\n"
            "第一行（最上面前方有黃冠圖標）的是隊長！請嚴格遵循以下格式回傳：\n"
            "[LEADER] 隊長名字\n"
            "[MEMBER] 隊員名字\n"
            "[MEMBER] 隊員名字"
        )
        response = model.generate_content([prompt, img])
        # 釋放圖片記憶體
        img.close()
        return {"filename": filename, "status": "SUCCESS", "text": response.text}
    except Exception as e:
        return {"filename": filename, "status": "FAILED", "text": str(e)}

# =====================================================================
# 5. 主介面
# =====================================================================
st.markdown("<div class='clan-header'><div class='clan-title'>🏰 狂盟血誓戰盟 - 100圖重工業鐵血控制台 V44</div><div class='clan-subtitle'>CENTURY PARALLEL MATRIX PARSING SYSTEM • ULTIMATE VERSION</div></div>", unsafe_allow_html=True)

if not VALID_NAMES:
    st.error("🚨 報告老大：系統檢測到目前雲端成員資料庫抓取為空！請確認 CSV 網址。")
else:
    st.markdown("<div class='section-tag'>📸 戰場百圖大會戰熔爐 (💡 支援 100 張以上影像全自動無損通關)</div>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("請直接全選今天出團的所有小隊截圖（上限支援至 100+ 張）：", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

    if uploaded_files:
        st.success(f"📈 報告老大：成功載入 {len(uploaded_files)} 張戰場影像！鋼鐵抗壓引擎已鎖定目標。")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔥 啟動終極大熔爐！100張照片全自動地毯式點名", key="attack_btn", use_container_width=True):
        if not API_KEYS_POOL:
            st.error("⚠️ 老大！請先在左側邊欄輸入 狂盟核心 API 金鑰庫（百圖強烈建議輸入 3 組以上免費金鑰）！")
        elif not uploaded_files:
            st.warning("⚠️ 老大，您還沒有丟任何戰場截圖進來啊！")
        else:
            # 建立動態進度展示區
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            # 準備任務參數（將檔案轉為 Byte 流，降低持久記憶體佔用）
            tasks_args = []
            num_keys = len(API_KEYS_POOL)
            
            for idx, f in enumerate(uploaded_files):
                f.seek(0)
                file_bytes = f.read()
                selected_key = API_KEYS_POOL[idx % num_keys]
                # 智慧節流：每隔 4 張圖微幅增加 0.2 秒延遲，防止瞬間併發流量過大被 Google 阻斷
                delay = (idx // 4) * 0.2
                tasks_args.append((file_bytes, f.name, selected_key, delay))
            
            results = []
            total_tasks = len(tasks_args)
            
            # 使用 ThreadPoolExecutor 進行異步控速點火
            # 大批次圖片 max_workers 設為 6-8 最穩健，速度與安全兼具
            with ThreadPoolExecutor(max_workers=6) as executor:
                future_to_filename = {executor.submit(process_single_image, arg): arg[1] for arg in tasks_args}
                
                completed_count = 0
                for future in as_completed(future_to_filename):
                    completed_count += 1
                    res = future.result()
                    results.append(res)
                    
                    # 即時回報戰況給老大看，絕不打瞌睡
                    pct = completed_count / total_tasks
                    progress_bar.progress(pct)
                    status_text.markdown(f"<b style='color:#ffcc00;'>⚡ 鐵血抗壓熔爐運轉中：已完美解析 {completed_count} / {total_tasks} 張截圖... 戰場進度 {int(pct*100)}%</b>", unsafe_allow_html=True)
            
            status_text.markdown("<b style='color:#00ffcc;'>✅ 報告老大：100張大會戰截圖已全數平行解析完畢！正在生成總成果報表...</b>", unsafe_allow_html=True)
            
            # =====================================================================
            # 6. 整合生成最終大總表
            # =====================================================================
            report_html = "<div class='report-box'><div class='section-tag' style='background:none; border:none; padding:0; color:#ff0000; font-size:20px;'>🦅 狂盟百圖會戰 - 終極大總表</div>"
            
            global_excel_idx = 1
            raw_text_report = ""
            REGISTERED_NAMES_POOL = set()
            
            # 依據檔名排序輸出，確保報表整齊
            results_sorted = sorted(results, key=lambda x: x["filename"])
            
            for res in results_sorted:
                filename = res["filename"]
                d_row, t_row, tg_row, cmd_row, tm_row = parse_filename_data(filename)
                
                report_html += f"""
                <div style='margin-top:12px; background-color:#121216; padding:8px; border-left:4px solid #ff0000;'>
                    <span style='color:#ff0000; font-weight:bold;'>📸 分隊 {tm_row}</span> <span style='color:#888; font-size:12px;'>({filename})</span> | 
                    <span style='color:#aaa; font-size:13px;'>{d_row} | {t_row} | 目標: {tg_row} | 統帥: {cmd_row}</span>
                </div><br>
                """
                
                if res["status"] == "FAILED":
                    report_html += f"<div class='unconfirmed-red'>❌ 該圖片解析失敗：{res['text']}</div>"
                    continue
                    
                local_idx = 1
                lines = res["text"].strip().split('\n')
                for line in lines:
                    cleaned = line.replace("[LEADER]", "").replace("[MEMBER]", "").replace(" ", "").strip()
                    if not cleaned or "---" in cleaned: continue
                    
                    final_name, match_status, hint_msg = smart_match_name(cleaned, VALID_NAMES)
                    is_leader = "[LEADER]" in line or local_idx == 1
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
                st.markdown("<br><div class='section-tag'>📋 狂盟直貼 Excel 數據中心 (完美統合百圖 7 大直欄)</div>", unsafe_allow_html=True)
                st.text_area("", value=raw_text_report.strip(), height=300, key="copy_target", label_visibility="collapsed")
                
                escaped_text = raw_text_report.strip().replace("`", "\\`").replace("'", "\\'")
                js_button_html = f"""
                <div style="text-align: center; width: 100%;">
                    <button onclick="navigator.clipboard.writeText(`{escaped_text}`).then(() => alert('📋 報告老大：V44 百圖會戰終極數據已全數統合複製！'));" 
                    style="width: 100%; background: linear-gradient(180deg, #cc0000 0%, #880000 100%); color: white; border: 2px solid #d4af37; padding: 18px; font-size: 18px; font-weight: bold; border-radius: 6px; cursor: pointer; box-shadow: 0 6px 15px rgba(255,0,0,0.4); letter-spacing:2px;">
                        🦅 一鍵秒複製 100 圖巨量統合數據 🦅
                    </button>
                </div>
                """
                st.components.v1.html(js_button_html, height=80)
