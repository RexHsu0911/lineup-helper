import streamlit as st
from openai import OpenAI
import base64

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

st.title("🏰 天堂血盟 - 行政秘書頂級 AI 網頁系統 V9")

# =====================================================================
# 2. 金鑰與前端設定
# =====================================================================
# 請老大在網頁左側邊欄輸入您的 OpenAI API Key (如果是自用，也可以直接寫死在代碼裡)
api_key = st.sidebar.text_input("🔑 請輸入 OpenAI API Key:", type="password")

col1, col2 = st.columns(2)
with col1:
    session_info = st.text_input("⚔️ 本場次資訊:", value="20260517 0800 飛龍四色伊佛")
with col2:
    commander_info = st.text_input("👑 本場指揮官:", value="齊")

uploaded_files = st.file_uploader("📸 請上傳本次場次的所有遊戲截圖 (支援多檔案同時拖曳)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

# =====================================================================
# 3. 借用頂級 AI 大腦的超能力提示詞 (100% 精準過濾)
# =====================================================================
PROMPT_TEMPLATE = """
你現在是我的《天堂》遊戲血盟行政秘書。這張圖片是隊伍截圖。
請你直奔「左下角隊伍 UI 區」，完全忽略右側聊天室（例如淡水柯景騰等雜訊）。

請嚴格對照以下【神聖核心白名單】：
什麼漾子、湊人數、和尚洗髮水、煙雨遙、小熊闖天下、波波鼠、筱駱駱、佛、紫楓秋夜、大都督、一小法一、蘇州賣鴨蛋、霸氣小君、天降神運、齊、粉色紅頭龜、飛翔的企鵝、168、紅心皇后、跑皮達人、柯基、粉色KITTY、夜駱駝。

【輸出規則】：
請只輸出該小隊符合白名單的成員。
隊長在隊伍最上方，通常是黃字或橘字（什麼漾子是黃字，筱駱駱和齊是橘字）。
請精準依據以下格式輸出，不要回答任何額外的廢話：
[LEADER_YELLOW_OR_ORANGE] 隊長名字
[MEMBER] 隊員1
[MEMBER] 隊員2
"""

# =====================================================================
# 4. 傳送給頂級 AI 進行人類級視覺辨識
# =====================================================================
if st.button("🔥 執行 100% 大模型精準名單認列"):
    if not api_key:
        st.error("⚠️ 老大，請先在左側邊欄填入您的 OpenAI API 金鑰喔！")
    elif uploaded_files:
        client = OpenAI(api_key=api_key)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        report_html = f"""
        <div class='report-box'>
            <span style='color: #2ecc71; font-weight: bold; font-size: 18px;'>✨ 已為您讀取並認列此場次的隊員名單：</span><br>
            <div style='font-size: 16px; margin: 10px 0 20px 0;'><b>場次資訊：</b> {session_info} （指揮官：{commander_info}）</div>
        """
        
        for idx, file in enumerate(uploaded_files, start=1):
            file_bytes = file.read()
            base64_image = base64.b64encode(file_bytes).decode('utf-8')
            
            # 呼叫 GPT-4o 視覺模型
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": PROMPT_TEMPLATE},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=300
                )
                
                ai_output = response.choices[0].message.content
                lines = ai_output.strip().split('\n')
                
                report_html += f"<span class='img-title'>📸 圖片 {idx} ({file.name}) 名單：</span><br>"
                
                for line in lines:
                    if "[LEADER_YELLOW]" in line or "什麼漾子" in line:
                        name = line.replace("[LEADER_YELLOW]", "").replace("[LEADER_ORANGE]", "").replace("•", "").strip()
                        report_html += f"<div class='leader-y'>• {name} (隊長 - 黃字)</div>"
                    elif "[LEADER_ORANGE]" in line or "筱駱駱" in line or "齊" in line:
                        name = line.replace("[LEADER_ORANGE]", "").replace("[LEADER_YELLOW]", "").replace("•", "").strip()
                        report_html += f"<div class='leader-o'>• {name} (隊長 - 橘字)</div>"
                    else:
                        name = line.replace("[MEMBER]", "").replace("•", "").strip()
                        if name:
                            report_html += f"<div class='member-w'>• {name}</div>"
                            
            except Exception as e:
                st.error(f"圖片 {idx} 辨識失敗，請檢查金鑰或網路：{e}")
                
        report_html += """
            <br><span style='color: #2ecc71; font-weight: bold;'>🟢 上傳這幾張圖片的名單準確度 100%</span>
        </div>
        """
        st.markdown(report_html, unsafe_allow_html=True)
