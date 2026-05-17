import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import datetime
import itertools
import time

# =====================================================================
# 1. 網頁頂級【天堂經典 - 狂盟金黑神殿】視覺風格 (CSS)
# =====================================================================
st.markdown("""
    <style>
    /* 全域背景顏色：深淵黑 */
    .stApp { background-color: #0d0d0d; color: #ffffff; }
    
    /* 標題：古董金 */
    h1 { color: #f1c40f; text-align: center; font-family: 'Microsoft JhengHei', sans-serif; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    
    /* 側邊欄：黑金剛 */
    .stSidebar { background-color: #1a1a1a; border-right: 1px solid #d4af37; }
    
    /* 網頁端辨識結果框：金屬黑框 + 古董金邊 */
    .report-box { background-color: #111111; border: 2px solid #d4af37; padding: 25px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.6); }
    
    /* 小隊圖片標題：深邃藍 */
    .img-title { color: #3498db; font-weight: bold; font-size: 16px; margin-top: 20px; display: block; border-left: 4px solid #3498db; padding-left: 10px; }
    
    /* 黃字隊長：聖光金 */
    .leader-y { color: #f1c40f; font-weight: bold; padding-left: 20px; }
    
    /* 橘字隊長：勇者橘 */
    .leader-o { color: #e67e22; font-weight: bold; padding-left: 20px; }
    
    /* 隊員：淨白 */
    .member-w { color: #ffffff; padding-left: 20px; margin: 4px 0; }
    
    /* 水平分割線顏色 */
    hr { border: 0; border-top: 1px solid #333; }
    
    /* 輸入欄位樣式優化 */
    .stDateInput, .stSelectbox, .stTextInput { border-color: #444; color: #fff; }
    
    /* 下載按鈕（偽複製按鈕）預設樣式：海軍綠 */
    .copy-btn { width: 100%; background-color: #16a085; color: white; border: none; padding: 15px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .copy-btn:hover { background-color: #1abc9c; }
    </style>
""", unsafe_allow_html=True)

st.title("🏰 天堂血盟 - 行政秘書免費 AI 網頁系統 V17")

# =====================================================================
# 2. 核心大名單與選單設置
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

VALID_NAMES = [
    "什麼漾子", "湊人數", "和尚洗髮水", "煙雨遙", "小熊闖天下", "波波鼠", 
    "筱駱駱", "佛", "紫楓秋夜", "大都督", "一小法一", "蘇州賣鴨蛋", "霸氣小君", "霸气小君", "天降神運", 
    "齊", "粉色紅頭龜", "飛翔的企鵝", "168", "紅心皇后", "跑皮達人", "柯基", "粉色KITTY", "夜駱駝"
]

# 初始化記憶庫
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# =====================================================================
# 3. 前端選單輸入區
# =====================================================================
st.sidebar.markdown("<h2 style='color:#f1c40f;'>🔑 金鑰設定</h2>", unsafe_allow_html=True)
api_key = st.sidebar.text_input("請輸入 Google Gemini API Key:", type="password")

st.markdown("<b style='color:#f1c40f; font-size:16px;'>⚔️ 參戰資訊設定：</b>", unsafe_allow_html=True)

col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input("📅 選擇日期:", datetime.date(2026, 5, 17))
with col_time:
    time_options = [f"{str(h).zfill(2)}00" for h in range(24)]
    selected_time = st.selectbox("⏰ 選擇時間:", options=time_options, index=8)

col_target, col_cmd = st.columns(2)
with col_target:
    selected_target = st.selectbox("🎯 出團目標:", options=all_combinations)
with col_cmd:
    selected_commander = st.selectbox("👑 本場指揮官:", options=COMMANDER_LIST, index=0)

st.markdown("<hr>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "📸 請上傳本次場次的所有遊戲截圖", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg'],
    key=f"uploader_{st.session_state.uploader_key}"
)

# 圖片縮圖預覽
if uploaded_files:
    st.markdown("<b style='color:#3498db;'>🖼️ 已上傳圖片縮圖預覽：</b>", unsafe_allow_html=True)
    preview_cols = st.columns(min(len(uploaded_files), 4))
    for idx, file in enumerate(uploaded_files):
        with preview_cols[idx % 4]:
            file_bytes = file.read()
            file.seek(0)
            img_preview = Image.open(io.BytesIO(file_bytes))
            st.image(img_preview, caption=f"圖片 {idx+1}", use_container_width=True)

# =====================================================================
# 4. 【修復】圖片 3 漏隊長「齊」之鋼鐵律令提示詞
# =====================================================================
PROMPT_TEMPLATE = """
你現在是《天堂》遊戲血盟行政秘書。這張圖是隊伍截圖。
請你直奔圖片「左下角隊伍 UI 區」，完全忽略右側聊天室（例如淡水柯景騰等雜訊）。

請嚴格、逐字對照以下【神盛核心白名單】：
什麼漾子、湊人數、和尚洗髮水、煙雨遙、小熊闖天下、波波鼠、筱駱駱、佛、紫楓秋夜、大都督、一小法一、蘇州賣鴨蛋、霸气小君、霸氣小君、天降神運、齊、粉色紅頭龜、飛翔的企鵝、168、紅心皇后、跑皮達人、柯基、粉色KITTY、夜駱駝。

【💀 鋼鐵律令：單字隊長必須抓出】
小隊最上方的第一個名字是隊長。
即使該名字只有一個字（例如「齊」），你也必須把「齊」抓出來，排在名單的第一行，絕對不准漏掉！絕對不准！

【🛡️ 鐵律：字體外觀注意】
請原封不動地輸出圖片中的字，如果是簡體的「霸气小君」，就必須輸出「霸气小君」，絕對不准擅自改成繁體！

【輸出格式】：
請精準依據以下格式輸出，名字後面括號寫(隊長)即可，不要回答任何額外的廢話：
[LEADER] 隊長名字
[MEMBER] 隊員1
[MEMBER] 隊員2
"""

# =====================================================================
# 5. 操作按鈕功能區（金黑配色）
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2 = st.columns(2)

# =====================================================================
# 6. 【防呆】執行時按鈕變灰並禁用
# =====================================================================
if 'running' not in st.session_state:
    st.session_state.running = False

def set_running_true():
    st.session_state.running = True

with btn_col1:
    execute_button = st.button(
        "🔥 執行大模型精準認列", 
        use_container_width=True, 
        key="exec_btn",
        on_click=set_running_true,
        disabled=st.session_state.running
    )

with btn_col2:
    # 清除鍵也加上狂盟風格樣式
    if st.button("🔄 清除本場 / 準備下一場", use_container_width=True, key="clear_btn"):
        st.session_state.uploader_key += 1
        # 確保重置時 running 狀態也恢復
        st.session_state.running = False
        st.rerun()

# =====================================================================
# 7. 核心處理與報告輸出
# =====================================================================
# 只有在按鈕被點擊，且 running 為 True 時才執行辨識
if st.session_state.running and execute_button:
    if not api_key:
        st.error("⚠️ 老大，請先在左側邊欄填入您的 Google API 金鑰喔！")
        # 恢復按鈕狀態
        st.session_state.running = False
        st.rerun()
    elif uploaded_files:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        date_str = selected_date.strftime("%Y%m%d")
        raw_text_report = "" # 用於 Excel 貼上格式數據
        
        # 網頁圖形化顯示的總標題
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
        
        excel_global_idx = 1 # 用於 Excel 流水號 (全場打散統一)
        
        for idx, file in enumerate(uploaded_files, start=1):
            file.seek(0)
            file_bytes = file.read()
            pil_image = Image.open(io.BytesIO(file_bytes))
            
            try:
                # 執行 Gemini 2.5 Flash 辨識
                response = model.generate_content([PROMPT_TEMPLATE, pil_image])
                ai_output = response.text
                lines = ai_output.strip().split('\n')
                
                # 網頁端顯示：每張圖片各自認列小隊分組與序號
                report_html += f"<span class='img-title'>📸 圖片 {idx} ({file.name}) 名單：</span><br>"
                
                team_local_idx = 1 # 網頁端小隊內部獨立序號 (1-8)
                
                for line in lines:
                    clean_line = line.replace("[LEADER]", "").replace("[MEMBER]", "").replace("•", "").replace("•", "").strip()
                    name_only = clean_line.split("(")[0].strip()
                    
                    if name_only in VALID_NAMES:
                        # 1. 🌟 用於 Excel 貼上格式數據 (流水號定位A欄)
                        # 核心公式：序號 \t 日期 \t 時間 \t 出團目標 \t 指揮官 \t 成員名單 \t 職位
                        excel_row_base = f"{excel_global_idx}\t{date_str}\t{selected_time}\t{selected_target}\t{selected_commander}\t{name_only}"
                        
                        # 2. 用於網頁圖形辨識結果顯示
                        if name_only in ["什麼漾子", "筱駱駱", "齊"] or "(隊長)" in clean_line:
                            if name_only == "什麼漾子":
                                report_html += f"<div class='leader-y'>{team_local_idx}. {name_only} (隊長)</div>"
                            else:
                                report_html += f"<div class='leader-o'>{team_local_idx}. {name_only} (隊長)</div>"
                            # 寫入 Excel 複製字串
                            raw_text_report += f"{excel_row_base}\t隊長\n"
                        else:
                            report_html += f"<div class='member-w'>{team_local_idx}. {name_only}</div>"
                            raw_text_report += f"{excel_row_base}\t\n" # 隊員職位留空
                        
                        team_local_idx += 1
                        excel_global_idx += 1 # 全球流水號也同步加
                        
            except Exception as e:
                st.error(f"圖片 {idx} 辨識出錯：{e}")
                
        report_html += "</div>"
        
        # 1. 網頁渲染精美結果
        st.markdown(report_html, unsafe_allow_html=True)
        
        # 2. 顯示純文字複製框
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_area("📋 下方為專用 Excel 貼上格式數據（7大欄位）：", value=raw_text_report.strip(), height=250, key="copy_target")
        
        # 3. 🌟 無敵 JavaScript 一鍵複製大按鈕（配合狂盟樣式）
        escaped_text = raw_text_report.strip().replace("`", "\\`").replace("'", "\\'")
        js_button_html = f"""
        <div style="text-align: center; width: 100%;">
            <button class="copy-btn" onclick="navigator.clipboard.writeText(`{escaped_text}`).then(() => alert('📋 報告老大：Excel 7大欄位專用數據已複製！'));" >
                📋 點我一鍵複製 Excel 7大欄位數據
            </button>
        </div>
        """
        st.components.v1.html(js_button_html, height=70)
        
        # 恢復按鈕狀態，以便下次執行
        st.session_state.running = False
        st.rerun()
