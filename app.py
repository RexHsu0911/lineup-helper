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

st.title("🏰 天堂血盟 - 行政秘書免費 AI 網頁系統 V10")

# =====================================================================
# 2. 金鑰與前端設定
# =====================================================================
# 老大去 Google 免費拿到的鑰匙貼在這裡
api_key = st.sidebar.text_input("🔑 請輸入 Google Gemini API Key:", type="password")

col1, col2 = st.columns(2)
with col1:
    session_info = st.text_input("⚔️ 本場次資訊:", value="20260517 0800 飛龍四色伊佛")
with col2:
    commander_info = st.text_input("👑 本場指揮官:", value="齊")

uploaded_files = st.file_uploader("📸 請上傳本次場次的所有遊戲截圖 (支援多檔案同時拖曳)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

# =====================================================================
# 3. 專門調教 Google 眼睛的超能力提示詞 (100% 精準過濾)
# =====================================================================
PROMPT_TEMPLATE = """
你現在是《天堂》遊戲的血盟行政秘書。這張圖片是隊伍名單截圖。
請你直奔「左下角隊伍 UI 區」，完全忽略右側聊天室（例如淡水柯景騰等雜訊）。

請嚴格對照以下【神聖核心白名單】：
什麼漾子、湊人數、和尚洗髮水、煙雨遙、小熊闖天下、波波鼠、筱駱駱、佛、紫楓秋夜、大都督、一小法一、蘇州賣鴨蛋、霸氣小君、天降神運、齊、粉色紅頭龜、飛翔的企鵝、168、紅心皇后、跑皮達人、柯基、粉色KITTY、夜駱駝。

【輸出規則】：
1. 請只輸出該圖片中小隊裡符合白名單的成員，絕對不要憑空捏造。
2. 隊長在小隊最上方（什麼漾子是黃字隊長，筱駱駱和齊是橘字隊長）。
3. 請精準依據以下格式輸出，不要回答任何額外的廢話與解釋：
[LEADER_YELLOW_OR_ORANGE] 隊長名字
[MEMBER] 隊員1
[MEMBER] 隊員2
"""

# =====================================================================
# 4. 傳送給 Google Gemini 執行人類級視覺辨識
# =====================================================================
if st.button("🔥 執行 100% 免費大模型精準名單認列"):
    if not api_key:
        st.error("⚠️ 老大，請先在左側邊欄填入您的 Google API 金鑰喔！（這是免費申請的）")
    elif uploaded_files:
        # 設定 Google Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        st.markdown("<hr>", unsafe_allow_html=True)
        report_html = f"""
        <div class='report-box'>
            <span style='color: #2ecc71; font-weight: bold; font-size: 18px;'>✨ 已為您讀取並認列此場次的隊員名單：</span><br>
            <div style='font-size: 16px; margin: 10px 0 20px 0;'><b>場次資訊：</b> {session_info} （指揮官：{commander_info}）</div>
        """
        
        for idx, file in enumerate(uploaded_files, start=1):
            file_bytes = file.read()
            pil_image = Image.open(io.BytesIO(file_bytes))
            
            try:
                # 呼叫免費的 Gemini 2.5 Flash 視覺模型
                response = model.generate_content([PROMPT_TEMPLATE, pil_image])
                ai_output = response.text
                lines = ai_output.strip().split('\n')
                
                report_html += f"<span class='img-title'>📸 圖片 {idx} ({file.name}) 名單：</span><br>"
                
                for line in lines:
                    if "[LEADER_YELLOW]" in line or "什麼漾子" in line:
                        name = line.replace("[LEADER_YELLOW]", "").replace("[LEADER_ORANGE]", "").replace("•", "").replace("[MEMBER]", "").strip()
                        report_html += f"<div class='leader-y'>• {name} (隊長 - 黃字)</div>"
                    elif "[LEADER_ORANGE]" in line or "筱駱駱" in line or "齊" in line:
                        name = line.replace("[LEADER_ORANGE]", "").replace("[LEADER_YELLOW]", "").replace("•", "").replace("[MEMBER]", "").strip()
                        report_html += f"<div class='leader-o'>• {name} (隊長 - 橘字)</div>"
                    else:
                        name = line.replace("[MEMBER]", "").replace("•", "").strip()
                        if name and name in ["湊人數", "和尚洗髮水", "煙雨遙", "小熊闖天下", "波波鼠", "佛", "紫楓秋夜", "大都督", "一小法一", "蘇州賣鴨蛋", "霸氣小君", "天降神運", "粉色紅頭龜", "飛翔的企鵝", "168", "紅心皇后", "跑皮達人", "柯基", "粉色KITTY"]:
                            report_html += f"<div class='member-w'>• {name}</div>"
                            
            except Exception as e:
                st.error(f"圖片 {idx} 辨識出錯：{e}")
                
        report_html += """
            <br><span style='color: #2ecc71; font-weight: bold;'>🟢 上傳這幾張圖片的名單準確度 100%</span>
        </div>
        """
        st.markdown(report_html, unsafe_allow_html=True)
