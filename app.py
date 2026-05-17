import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import datetime
import itertools

# 配置網頁分頁標題與圖示
st.set_page_config(page_title="狂盟血盟後台系統", page_icon="🏰", layout="wide")

# =====================================================================
# 1. 狂盟尊爵：天堂經典血誓不朽視覺風格 (CSS 究極魔改版)
# =====================================================================
st.markdown("""
    <style>
    /* 全局戰場迷霧深黑 */
    .main { 
        background-color: #08080a; 
        color: #e0e0e0; 
        font-family: 'Microsoft JhengHei', 'Segoe UI', sans-serif; 
    }
    
    /* 側邊欄高端鐵冷色 */
    [data-testid="stSidebar"] {
        background-color: #0c0c0e !important;
        border-right: 2px solid #8c7323;
    }
    
    /* 標題區：狂盟血誓神殿大門 */
    .clan-header {
        background: linear-gradient(90deg, rgba(179,0,0,0.2) 0%, rgba(0,0,0,0.8) 50%, rgba(179,0,0,0.2) 100%);
        border: 2px solid #9a7b2c;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 20px rgba(179,0,0,0.4);
    }
    .clan-title { 
        color: #ff0000; 
        font-weight: 900; 
        font-size: 36px;
        text-shadow: 3px 3px 5px #000000, 0 0 25px #ff0000; 
        letter-spacing: 4px;
        margin: 0;
    }
    .clan-subtitle {
        color: #9a7b2c;
        font-size: 14px;
        letter-spacing: 2px;
        margin-top: 5px;
        font-weight: bold;
    }
    
    /* 皇家暗金立體報告箱 */
    .report-box { 
        background: linear-gradient(145deg, #111114, #16161b);
        border: 2px solid #9a7b2c; 
        padding: 30px; 
        border-radius: 8px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.9), 0 0 15px rgba(154,123,44,0.2);
    }
    
    /* 區塊核心發光標題 */
    .section-tag {
        color: #ffffff;
        font-size: 18px;
        font-weight: bold;
        background: linear-gradient(90deg, #b30000 0%, transparent 100%);
        padding: 6px 15px;
        border-radius: 4px;
        margin-bottom: 20px;
        border-left: 5px solid #ff0000;
        text-shadow: 1px 1px 2px #000;
    }
    
    /* 圖片分隊卡片 */
    .img-title { 
        color: #ffcc00; 
        font-weight: bold; 
        font-size: 16px; 
        margin-top: 25px; 
        display: block;
        border-bottom: 1px solid #443615;
        padding-bottom: 5px;
    }
    
    /* 隊長與隊員字體升級 */
    .leader-y { color: #ff9900; font-weight: bold; padding-left: 20px; font-size: 16px; margin: 6px 0; text-shadow: 1px 1px 3px #000; }
    .leader-o { color: #ff5500; font-weight: bold; padding-left: 20px; font-size: 16px; margin: 6px 0; text-shadow: 1px 1px 3px #000; }
    .member-w { color: #e0e0e0; padding-left: 20px; margin: 5px 0; font-size: 15px; }
    
    /* 修改所有預設 Label 顏色為暗金 */
    label { 
        color: #9a7b2c !important; 
        font-weight: bold !important; 
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* 輸入框高階工程師黑鐵化與動態發光 */
    input, select, div[data-baseweb="select"], div[data-baseweb="input"] {
        background-color: #121215 !important;
        color: #ffffff !important;
        border: 1px solid #9a7b2c !important;
        border-radius: 4px !important;
    }
    
    /* 覆魔客製化：上傳檔案區 */
    div[data-testid="stFileUploader"] {
        background-color: #0f0f12;
        border: 2px dashed #b30000 !important;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* =====================================================================
    /* 💥 狂盟專屬付費級頂級按鈕魔改 (CSS injection)
    /* ===================================================================== */
    /* 1. 烈焰攻城按鈕 */
    div.stButton > button[key="attack_btn"] {
        background: linear-gradient(180deg, #ff0000 0%, #880000 100%) !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        border: 2px solid #ffcc00 !important;
        box-shadow: 0 0 15px rgba(255,0,0,0.6) !important;
        text-shadow: 2px 2px 4px #000000 !important;
        letter-spacing: 2px !important;
        transition: all 0.3s ease !important;
        height: 55px !important;
        border-radius: 6px !important;
    }
    div.stButton > button[key="attack_btn"]:hover {
        background: linear-gradient(180deg, #ff3333 0%, #aa0000 100%) !important;
        box-shadow: 0 0 25px rgba(255,0,0,0.9) !important;
        transform: translateY(-2px);
    }
    
    /* 2. 戰場餘燼清理按鈕 */
    div.stButton > button[key="reset_btn"] {
        background: linear-gradient(180deg, #2a2a2e 0%, #161618 100%) !important;
        color: #9a7b2c !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: 1px solid #443615 !important;
        text-shadow: 1px 1px 2px
