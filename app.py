import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 頁面設定 (必須放在第一行) ---
st.set_page_config(
    page_title="VisualAdapt AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS 美化 (讓介面更像 App) ---
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
    /* 隱藏預設選單 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. 側邊欄：API Key 設定 ---
with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input("Google Gemini API Key", type="password", placeholder="請在此貼上您的 API Key")
    
    if not api_key:
        st.warning("⚠️ 請先輸入 API Key 才能使用。")
        st.markdown("[👉 點此獲取 API Key](https://aistudio.google.com/app/apikey)")
    
    st.markdown("---")
    st.markdown("### 關於本工具")
    st.info(
        "這是一個專為創作者設計的 AI 輔助工具，能自動生成適配不同社群平台的排版指令。"
    )

# --- 4. 主標題 ---
st.title("🎨 VisualAdapt AI")
st.markdown("### 跨平台縮圖與專輯封面適配器")

# --- 5. 核心邏輯 (包含最強版的 System Prompt) ---
def get_gemini_response(image, platform, resolution=None, extra_instruction=""):
    if not api_key:
        return "⚠️ Error: 請先在左側邊欄輸入 Google Gemini API Key"
    
    genai.configure(api_key=api_key)
    
    # 這裡整合了之前的「強制重排版」與「解析度控制」邏輯
    sys_instruction = """
    **角色定義：**
    你是一位精通「跨平台視覺重構」與「生圖參數工程」的 AI 技術總監。你的核心任務是分析使用者上傳的圖片，並輸出「精確的生圖提示詞 (Prompt)」，指揮後端模型進行畫面重構。

    **核心任務 (Mission)：**
    1.  **拒絕無效變形：** 確保輸出包含嚴格的寬高比參數。
    2.  **拒絕簡單填充：** 當畫面比例發生劇烈變化（如橫轉直）時，必須指揮模型進行「解構與重組 (Deconstruct & Recompose)」，而非簡單的背景擴充。

    **標準作業程序 (SOP)：**

    **第一步：構建重構策略**
    * **場景 A：橫圖轉直圖 (如 YouTube -> TikTok)**
        * **禁止：** 禁止只使用 "Expand background"。
        * **強制：** 使用 "Shift and Scale" (位移與縮放)。
        * **指令邏輯：** "Crop the text layer and move it to the top safe zone. Enlarge the main character to fill the width. Regenerate the background to connect them."
    * **場景 B：專輯封面 / IG (1:1)**
        * **強制：** 必須將 [Target Resolution] 參數加入指令中，確保高畫質輸出。

    **第二步：輸出標準化指令 (JSON 格式)**
    你必須輸出以下格式：
    {
        "platform": "[平台名稱]",
        "aspect_ratio": "[比例]",
        "resolution_target": "[解析度]",
        "prompt": "[給生圖模型的詳細英文提示詞]"
    }
    """
    
    model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=sys_instruction)
    
    # 建構使用者請求
    user_prompt = f"我的目標平台是：{platform}。"
    if resolution:
        user_prompt += f" 請強制輸出解析度為：{resolution}。"
    if extra_instruction:
        user_prompt += f" 額外使用者要求：{extra
