import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import datetime
import itertools
import time
import pandas as pd

# 配置網頁分頁標題與圖示
st.set_page_config(page_title="狂盟血盟後台系統", page_icon="🏰", layout="wide")

# =====================================================================
# 1. 狂盟尊爵：天堂經典血誓不朽視覺風格 (CSS 究極魔改 V35 版)
# =====================================================================
st.markdown("""
    <style>
    /* 全局戰場迷霧深黑 */
    .main { 
        background-color: #060608; 
        color: #e5e5e7; 
        font-family: 'Microsoft JhengHei', 'Segoe UI', sans-serif; 
    }
    
    /* 側邊欄高端鐵冷色 */
    [data-testid="stSidebar"] {
        background-color: #0b0b0d !important;
        border-right: 3px solid #d4af37;
    }
    
    /* 標題區：狂盟血誓神殿大門 */
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
    
    /* 皇家暗金立體報告箱 */
    .report-box { 
        background: linear-gradient(145deg, #0f0f12, #15151a);
        border: 2px solid #d4af37; 
        padding: 35px; 
        border-radius: 10px; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.9), 0 0 20px rgba(212,175,55,0.15);
    }
    
    /* 區塊核心發光標題 */
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
    
    /* 圖片分隊卡片 */
    .img-title { 
        color: #ffcc00; 
        font-weight: bold; 
        font-size: 17px; 
        margin-top: 28px; 
        display: block;
        border-bottom: 2px solid #443615;
        padding-bottom: 6px;
    }
    
    /* 👑 隊長一律顯示為爆擊橘色 */
    .leader-orange { 
        color: #ff4500 !important; 
        font-weight: bold !important; 
        padding-left: 20px; 
        font-size: 17px; 
        margin: 8px 0; 
        text-shadow: 1px 1px 4px #000; 
    }
    .member-w { color: #e5e5e7; padding-left: 20px; margin: 6px 0; font-size: 16px; }
    
    /* 修改所有預設 Label 顏色為不朽金 */
    label { 
        color: #d4af37 !important; 
        font-weight: bold !important; 
        font-size: 16px !important;
        letter-spacing: 1px;
        text-shadow: 1px 1px 2px #000;
        margin-bottom: 8px !important;
    }
    
    /* 下拉選單與輸入框徹底移除游標小框框 */
    input, select, div[data-baseweb="select"], div[data-baseweb="input"], .stSelectbox, .stDateInput {
        background-color: #111114 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div[data-baseweb="select"] {
        border: 1px solid #d4af37 !important;
    }
    input {
        border: 1px solid #d4af37 !important;
        caret-color: transparent !important;
    }
    
    div[data-baseweb="select"]:focus-within, div[data-baseweb="input"]:focus-within, input:focus {
        border-color: #ff0000 !important;
        box-shadow: 0 0 14px rgba
