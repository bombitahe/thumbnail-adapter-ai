import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="VisualAdapt AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS 美化 ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #4F46E5;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    .stSelectbox, .stTextInput, .stTextArea {
        border-radius: 8px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. 側邊欄：API Key 設定 ---
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 嘗試從 Secrets 獲取 Key
    api_key = None
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ 已自動載入系統 API Key")
    else:
        api_key = st.text_input("Google Gemini API Key", type="password", placeholder="請在此貼上您的 API Key")
        if not api_key:
            st.warning("⚠️ 請輸入 Key 或在 Secrets 設定中配置")
            st.markdown("[👉 獲取 API Key](https://aistudio.google.com/app/apikey)")
    
    st.markdown("---")
    st.info("專為創作者設計，自動生成多平台適配指令。")

# --- 4. 主標題 ---
st.title("🎨 VisualAdapt AI")
st.markdown("### 跨平台縮圖與專輯封面適配器")

# --- 5. 核心邏輯 ---
def get_gemini_response(image, platform, resolution=None, extra_instruction=""):
    if not api_key:
        return "⚠️ Error: 未檢測到 API Key"
    
    genai.configure(api_key=api_key)
    
    sys_instruction = """
    **角色定義：**
    你是一位精通「跨平台視覺重構」的 AI 技術總監。
    
    **核心任務：**
    1.  **拒絕無效變形：** 輸出必須包含寬高比參數。
    2.  **拒絕簡單填充：** 當比例劇烈變化（如橫轉直），必須指揮模型進行「解構與重組 (Deconstruct & Recompose)」。
    
    **標準作業程序：**
    * **場景 A (橫轉直)：** 使用 "Shift and Scale"，移動文字至安全區，放大主體，重繪背景。
    * **場景 B (1:1/專輯)：** 必須包含 [Target Resolution] 參數。
    
    **輸出格式 (JSON)：**
    {
        "platform": "[平台名稱]",
        "aspect_ratio": "[比例]",
        "resolution_target": "[解析度]",
        "prompt": "[給生圖模型的詳細英文提示詞]"
    }
    """
    
    # --- 🔥 關鍵修改：使用更
