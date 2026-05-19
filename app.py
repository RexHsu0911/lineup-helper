import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import re
import difflib
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# 配置網頁分頁標題與圖示
st.set_page_config(page_title="狂盟血盟後台系統-究極版", page_icon="🏰", layout="wide")

# =====================================================================
# 1. 狂盟尊爵視覺風格 (CSS V43 究極無極限版)
# =====================================================================
st.markdown("""
    <style>
    .main { background-color: #060608; color: #e5e5e7; font-family: 'Microsoft JhengHei', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0b0b0d !important; border-right: 3px solid #d4af37; }
    .clan-header {
        background: linear-gradient(135deg, rgba(179,0,0,0.3) 0%, rgba(10,10,12,0.9) 50%, rgba(154,123,44,0.15) 100%);
        border: 2px solid #d4af37; border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 35px;
        box-shadow: 0 0 25px rgba(255,0,0,0.35), inset 0 0 20px rgba(212,175,55,0.1);
    }
    .clan-title { color: #ff0000; font-weight: 900; font-size: 40px; text-shadow: 3px 3px 6px #000000, 0 0 30px #ff0000, 0 0 10px #ffffff; letter-spacing: 5px; margin: 0; }
    .clan-subtitle { color: #d4af37; font-size: 15px; letter-spacing: 3px; margin-top: 8px; font-weight: bold; }
    .report-box { background: linear-gradient(145deg, #0f0f12, #15151a); border: 2px solid #d4af37; padding: 35px; border-radius: 10px; }
    .section-tag { color: #ffffff; font-size: 19px; font-weight: bold; background: linear-gradient(90deg, #b30000 0%, rgba(179,0,0,0.1) 70%, transparent 100%); padding: 8px 18px; border-radius: 4px; border-left: 6px solid #ff0000; }
    .filename-pill { background-color: #1a1a24; color: #00ffcc; border: 1px solid #00aa88; padding: 2px 8px; border-radius: 4px; font-family: monospace; }
    .leader-orange { color: #ff4500 !important; font-weight: bold !important; padding-left: 20px; font-size: 17px; margin: 4px 0; }
    .member-w { color: #e5e5e7; padding-left: 20px; margin: 4px 0; font-size: 16px; }
    .auto-corrected-yellow { color: #ffcc00 !important; font-weight: bold !important; padding-left: 20px; font-size: 16px; margin: 4px 0; }
    .unconfirmed-red { color: #ff0000 !important; font-weight: bold !important; padding-left: 20px; font-size: 16px; margin: 4px 0; }
    .suspect-hint { color: #8c8c9e !important; font-size: 13px !important; font-weight: normal !important; font-style: italic; }
    div.stButton > button[key="attack_btn"] {
        background: linear-gradient(180deg, #ff0000 0%, #aa0000 50%, #660000 100%) !important; color: #ffffff !important; font-weight: 900 !important; font-size: 22px !important;
        border: 2px solid #ffcc00 !important; box-shadow: 0 0 20px rgba(255,0,0,0.7) !important; height: 65px !important; border-radius: 8px !important;
    }
    .clan-table-container { border: 1px solid #d4af37; border-radius: 4px; overflow: hidden; }
    .clan-table { width: 100%; border-collapse: collapse; background-color: #0c0c0e; text-align: center; }
    .clan-table th { background: linear-gradient(180deg, #1a1a1e 0%, #0d0d10 100%); color: #d4af37; font-weight: bold; padding: 8px; border-bottom: 1px solid #33270c; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. 側邊欄配置 - 輪班 API 機制
# =====================================================================
st.sidebar.markdown("<h3 style='color:#d4af37; text-align:center;'>🏰 究極平行金鑰庫</h3>", unsafe_allow_html=True)
api_input = st.sidebar.text_area("🔑 請輸入金鑰（若有多組請用「分號;」或「逗號,」隔開）：", value="", help="若照片超過20張，建議放2-3組免費金鑰輪替")

# 解析多組 API keys
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
# 3. 核心解構與文字智慧碰撞演算法
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
# 4. 🚀 異步單圖處理器（平行宇宙發動核心）
# =====================================================================
def process_single_image(file_info, api_key_to_use):
    """單張圖片平行處理，保證 100% 精準度綁定"""
    file_bytes, filename = file_info
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
        return {"filename": filename, "status": "SUCCESS", "text": response.text}
    except Exception as e:
        return {"filename": filename, "status": "FAILED", "text": str(e)}

# =====================================================================
# 5. 主介面
# =====================================================================
st.markdown("<div class='clan-header'><div class='clan-title'>🏰 狂盟血誓戰盟 - 50圖平行矩陣究極控制台 V43</div><div class='clan-subtitle'>INFINITY PARALLEL MATRIX PARSING SYSTEM</div></div>", unsafe_allow_html=True)

if not VALID_NAMES:
    st.error("🚨 報告老大：系統檢測到目前雲端成員資料庫抓取為空！請確認 CSV 網址。")
else:
    st.markdown("<div class='section-tag'>📸 戰場大批次影像熔爐 (💡 支援50張以上照片一次無腦盲塞)</div>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("請全選您當天出團的所有截圖，直接拖曳進來：", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

    if uploaded_files:
        st.success(f"📈 報告老大：成功載入 {len(uploaded_files)} 張戰場影像！系統已準備好平行矩陣發動。")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔥 發動總攻擊！50張照片一秒全部點名認列", key="attack_btn", use_container_width=True):
        if not API_KEYS_POOL:
            st.error("⚠️ 老大！請先在左側邊欄輸入至少一組 狂盟核心 API 金鑰！")
        elif not uploaded_files:
            st.warning("⚠️ 老大，您還沒有丟任何戰場截圖進來啊！")
        else:
            with st.spinner("⚡ 矩陣超載啟動：平行異步發動，正在調度輪班金鑰全力解析中..."):
                # 準備異步任務資料
                prepared_tasks = []
                for f in uploaded_files:
                    f.seek(0)
                    prepared_tasks.append((f.read(), f.name))
                
                # 執行平行處理，金鑰自動輪班分配 (輪詢分配法)
                results = []
                num_keys = len(API_KEYS_POOL)
                
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    for idx, task in enumerate(prepared_tasks):
                        selected_key = API_KEYS_POOL[idx % num_keys] # 輪流用不同的 key 避免單一爆額度
                        futures.append(executor.submit(process_single_image, task, selected_key))
                    
                    for fut in futures:
                        results.append(fut.result())
                
                # =====================================================================
                # 6. 整合大會師成果報告
                # =====================================================================
                report_html = "<div class='report-box'><div class='section-tag' style='background:none; border:none; padding:0; color:#ff0000; font-size:20px;'>🦅 50圖平行矩陣大會師 - 完美統合成果</div>"
                
                global_excel_idx = 1
                raw_text_report = ""
                REGISTERED_NAMES_POOL = set()
                
                for res in results:
                    filename = res["filename"]
                    d_row, t_row, tg_row, cmd_row, tm_row = parse_filename_data(filename)
                    
                    report_html += f"""
                    <div style='margin-top:15px; background-color:#121216; padding:10px; border-left:4px solid #00ffcc;'>
                        <span style='color:#00ffcc; font-weight:bold;'>📸 戰術分隊 {tm_row}</span> <span style='color:#888; font-size:12px;'>({filename})</span><br>
                        <span style='color:#aaa; font-size:13px;'>日期: {d_row} | 時間: {t_row} | 目標: {tg_row} | 指揮官: {cmd_row}</span>
                    </div><br>
                    """
                    
                    if res["status"] == "FAILED":
                        report_html += f"<div class='unconfirmed-red'>❌ 該張圖片解析失敗：{res['text']}</div>"
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
                        
                        # 跨時空防重
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
                
                # 輸出大總表
                if raw_text_report:
                    st.markdown("<br><div class='section-tag'>📋 狂盟直貼 Excel 數據中心 (完美統合 7 大直欄)</div>", unsafe_allow_html=True)
                    st.text_area("", value=raw_text_report.strip(), height=300, key="copy_target", label_visibility="collapsed")
                    
                    escaped_text = raw_text_report.strip().replace("`", "\\`").replace("'", "\\'")
                    js_button_html = f"""
                    <div style="text-align: center; width: 100%;">
                        <button onclick="navigator.clipboard.writeText(`{escaped_text}`).then(() => alert('📋 報告老大：V43 50圖平行矩陣數據已全數統合完畢！已成功複製！'));" 
                        style="width: 100%; background: linear-gradient(180deg, #cc0000 0%, #880000 100%); color: white; border: 2px solid #d4af37; padding: 18px; font-size: 18px; font-weight: bold; border-radius: 6px; cursor: pointer; box-shadow: 0 6px 15px rgba(255,0,0,0.4); letter-spacing:2px;">
                            🦅 一鍵秒複製 50 圖究極統合數據 🦅
                        </button>
                    </div>
                    """
                    st.components.v1.html(js_button_html, height=80)
