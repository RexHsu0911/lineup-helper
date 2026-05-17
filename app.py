import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

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

st.title("🏰 天堂血盟 - 行政秘書免費 AI 網頁系統 V13")

# =====================================================================
# 2. 初始化記憶庫 (確保按清除鍵時能完美恢復預設)
# =====================================================================
if 'session_val' not in st.session_state:
    st.session_state.session_val = "20260517 0800 飛龍四色伊佛"
if 'commander_val' not in st.session_state:
    st.session_state.commander_val = "齊"
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# =====================================================================
# 3. 金鑰與前端設定
# =====================================================================
api_key = st.sidebar.text_input("🔑 請輸入 Google Gemini API Key:", type="password")

col1, col2 = st.columns(2)
with col1:
    session_info = st.text_input("⚔️ 本場次資訊:", value=st.session_state.session_val)
with col2:
    commander_info = st.text_input("👑 本場指揮官:", value=st.session_state.commander_val)

# 使用 uploader_key 來控制上傳元件，重置時清空已上傳檔案
uploaded_files = st.file_uploader(
    "📸 請上傳本次場次的所有遊戲截圖", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg'],
    key=f"uploader_{st.session_state.uploader_key}"
)

# =====================================================================
# 4. 鋼鐵律令提示詞
# =====================================================================
PROMPT_TEMPLATE = """
你現在是《天堂》遊戲的血盟行政秘書。這張圖片是隊伍名單截圖。
請你直奔「左下角隊伍 UI 區」，完全忽略右側聊天室（例如淡水柯景騰等雜訊）。

請嚴格、逐字對照以下【神盛核心白名單】：
什麼漾子、湊人數、和尚洗髮水、煙雨遙、小熊闖天下、波波鼠、筱駱駱、佛、紫楓秋夜、大都督、一小法一、蘇州賣鴨蛋、霸气小君、霸氣小君、天降神運、齊、粉色紅頭龜、飛翔的企鵝、168、紅心皇后、跑皮達人、柯基、粉色KITTY、夜駱駝。

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
# 5. 操作按鈕區（點擊認列 / 清除重置）
# =====================================================================
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    execute_click = st.button("🔥 執行 100% 免費大模型精準名單認列", use_container_width=True)

with btn_col2:
    # 🧹 老大要的清除鍵：一鍵恢復預設狀態！
    if st.button("🔄 清除本場 / 恢復預設準備下一場", use_container_width=True):
        st.session_state.session_val = "20260517 0800 飛龍四色伊佛"
        st.session_state.commander_val = "齊"
        st.session_state.uploader_key += 1  # 改變 key 會強迫上傳元件完全清空
        st.rerun()

# =====================================================================
# 6. 核心處理與報告輸出
# =====================================================================
if execute_click:
    if not api_key:
        st.error("⚠️ 老大，請先在左側邊欄填入您的 Google API 金鑰喔！")
    elif uploaded_files:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        raw_text_report = f"✨ 已為您讀取並認列此場次的隊員名單：\n場次資訊： {session_info} （指揮官：{commander_info}）\n\n"
        
        report_html = f"""
        <div class='report-box'>
            <span style='color: #2ecc71; font-weight: bold; font-size: 18px;'>✨ 已為您讀取並認列此場次的隊員名單：</span><br>
            <div style='font-size: 16px; margin: 10px 0 20px 0;'><b>場次資訊：</b> {session_info} （指揮官：{commander_info}）</div>
        """
        
        for idx, file in enumerate(uploaded_files, start=1):
            file_bytes = file.read()
            pil_image = Image.open(io.BytesIO(file_bytes))
            
            try:
                response = model.generate_content([PROMPT_TEMPLATE, pil_image])
                ai_output = response.text
                lines = ai_output.strip().split('\n')
                
                report_html += f"<span class='img-title'>📸 圖片 {idx} ({file.name}) 名單：</span><br>"
                raw_text_report += f"📸 圖片 {idx} ({file.name}) 名單：\n\n"
                
                member_idx = 1
                
                for line in lines:
                    clean_line = line.replace("[LEADER]", "").replace("[MEMBER]", "").replace("•", "").strip()
                    name_only = clean_line.split("(")[0].strip()
                    
                    if name_only in VALID_NAMES:
                        if name_only in ["什麼漾子", "筱駱駱", "齊"] or "(隊長)" in clean_line:
                            if name_only == "什麼漾子":
                                report_html += f"<div class='leader-y'>{member_idx}. {name_only} (隊長)</div>"
                            else:
                                report_html += f"<div class='leader-o'>{member_idx}. {name_only} (隊長)</div>"
                            raw_text_report += f"{member_idx}. {name_only} (隊長)\n"
                        else:
                            report_html += f"<div class='member-w'>{member_idx}. {name_only}</div>"
                            raw_text_report += f"{member_idx}. {name_only}\n"
                        
                        member_idx += 1
                        
                raw_text_report += "\n"
                
            except Exception as e:
                st.error(f"圖片 {idx} 辨識出錯：{e}")
                
        report_html += "</div>"
        
        # 1. 渲染網頁精美結果
        st.markdown(report_html, unsafe_allow_html=True)
        
        # 2. 顯示純文字結果框
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_area("📋 下方為可複製的純文字結果：", value=raw_text_report.strip(), height=250, key="copy_target")
        
        # 3. 🌟 終極無敵一鍵複製按鈕（保證按得到、按了秒複製）
        # 利用 JavaScript 寫死，大按鈕直接塞在文字框正下方，點了直接複製到剪貼簿！
        escaped_text = raw_text_report.strip().replace("`", "\\`").replace("'", "\\'")
        js_code = f"""
        <button onclick="navigator.clipboard.writeText(`{escaped_text}`).then(() => alert('📋 報告老大：名單已成功複製到剪貼簿！'));" 
        style="width: 100%; background-color: #16a085; color: white; border: none; padding: 12px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 10px;">
            📋 點我一鍵複製全文字名單
        </button>
        """
        st.components.v1.html(js_code, height=60)
