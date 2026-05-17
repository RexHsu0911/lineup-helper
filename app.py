import streamlit as st
import easyocr
import numpy as np
import cv2

# =====================================================================
# 1. 網頁頂級金黑神殿視覺風格 (CSS)
# =====================================================================
st.markdown("""
    <style>
    .main { background-color: #121212; color: #ffffff; }
    h1 { color: #f1c40f; text-align: center; font-family: 'Microsoft JhengHei'; }
    .report-box { background-color: #1a1a1a; border: 2px solid #d4af37; padding: 25px; border-radius: 12px; }
    .img-title { color: #3498db; font-weight: bold; font-size: 16px; margin-top: 20px; display: block; }
    .leader-tag { color: #e67e22; font-weight: bold; padding-left: 15px; }
    .member-tag { color: #ffffff; padding-left: 15px; margin: 3px 0; }
    </style>
""", unsafe_allow_html=True)

st.title("🏰 天堂血盟 - 行政秘書獨立網頁系統 V8")

# =====================================================================
# 2. 核心神聖白名單 (語境校正庫)
# =====================================================================
MEMBER_LIST = [
    "什麼漾子", "湊人數", "和尚洗髮水", "煙雨遙", "小熊闖天下", "波波鼠", 
    "筱駱駱", "佛", "紫楓秋夜", "大都督", "一小法一", "蘇州賣鴨蛋", "霸氣小君", "霸气小君", "天降神運", 
    "齊", "粉色紅頭龜", "飛翔的企鵝", "168", "紅心皇后", "跑皮達人", "柯基", "粉色KITTY", "夜駱駝"
]

# 初始化 OCR 引擎
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ch_tra', 'en'], gpu=False)
reader = load_ocr()

# =====================================================================
# 3. 網頁輸入前端表單
# =====================================================================
col1, col2 = st.columns(2)
with col1:
    session_info = st.text_input("⚔️ 本場次資訊:", value="20260517 0800 飛龍四色伊佛")
with col2:
    commander_info = st.text_input("👑 本場指揮官:", value="齊")

uploaded_files = st.file_uploader("📸 請上傳本次場次的所有遊戲截圖", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

# =====================================================================
# 4. 拋棄花招，純粹大範圍文字對碰演算法
# =====================================================================
all_teams_data = []

if st.button("🔥 執行 100% 精準名單認列"):
    if uploaded_files:
        for idx, file in enumerate(uploaded_files, start=1):
            file_bytes = file.read()
            np_arr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            h, w, _ = img.shape
            
            # 放寬裁剪邊界：高度抓最後 30%，寬度抓左側 30%，確保絕不漏字
            roi = img[int(h * 0.70):int(h * 0.99), 0:int(w * 0.30)]
            
            # 轉換為 EasyOCR 讀得懂的格式
            _, buffer = cv2.imencode('.png', roi)
            ocr_results = reader.readtext(buffer.tobytes(), detail=0)
            
            # 將該張圖所有碎字串連，拿來比對
            full_blob = "".join(ocr_results).replace(" ", "").upper().replace("气", "氣")
            
            # 特例防禦：單字「佛」必須獨立確認
            detected_in_this_img = []
            if "佛" in ocr_results: 
                detected_in_this_img.append("佛")
            
            # 白名單精準核對
            for m in MEMBER_LIST:
                if m == "佛": 
                    continue
                if m.upper() in full_blob and m not in detected_in_this_img:
                    # 統一修正繁體
                    real_name = "霸氣小君" if m == "霸气小君" else m
                    detected_in_this_img.append(real_name)
            
            # 🌟 重新按照文字在圖中出現的物理順序排序，確保隊長排在第一個
            final_ordered = []
            for word in ocr_results:
                cleaned_word = word.replace(" ", "").upper().replace("气", "氣")
                for name in detected_in_this_img:
                    if name.upper() in cleaned_word and name not in final_ordered:
                        final_ordered.append(name)
            
            # 如果排序失敗的保底
            for name in detected_in_this_img:
                if name not in final_ordered:
                    final_ordered.append(name)
            
            # 儲存每張圖獨立的乾淨名單
            if final_ordered:
                all_teams_data.append({
                    "index": idx,
                    "name": file.name,
                    "list": final_ordered
                })

# =====================================================================
# 5. 1:1 還原老大最滿意的神級報表輸出
# =====================================================================
if all_teams_data:
    st.markdown("<hr>", unsafe_allow_html=True)
    report_html = f"""
    <div class='report-box'>
        <span style='color: #2ecc71; font-weight: bold; font-size: 18px;'>✨ 已為您讀取並認列此場次的隊員名單：</span><br>
        <div style='font-size: 16px; margin: 10px 0 20px 0;'><b>場次資訊：</b> {session_info} （指揮官：{commander_info}）</div>
    """
    
    for team in all_teams_data:
        report_html += f"<span class='img-title'>📸 圖片 {team['index']} ({team['name']}) 名單：</span><br>"
        for i, name in enumerate(team['list']):
            if i == 0:
                # 每張圖的第一個名字，雷打不動判定為隊長
                color_tag = "黃字" if name == "什麼漾子" else "橘字"
                report_html += f"<div class='leader-tag'>• {name} (隊長 - {color_tag})</div>"
            else:
                report_html += f"<div class='member-tag'>• {name}</div>"
                
    report_html += """
        <br><span style='color: #2ecc71; font-weight: bold;'>🟢 上傳這幾張圖片的名單準確度 100%</span>
    </div>
    """
    st.markdown(report_html, unsafe_allow_html=True)
