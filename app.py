import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. 頁面設定 (必須放在第一行) ---
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

# --- 3. 側邊欄：智慧型 API Key 設定 ---
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 嘗試從 Secrets 獲取 Key
    api_key = None
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ 已自動載入系統 API Key")
    else:
        # 如果 Secrets 裡沒有，才顯示輸入框
        api_key = st.text_input("Google Gemini API Key", type="password", placeholder="請在此貼上您的 API Key")
        if not api_key:
            st.warning("⚠️ 請輸入 Key 或在 Secrets 設定中配置")
            st.markdown("[👉 獲取 API Key](https://aistudio.google.com/app/apikey)")
    
    st.markdown("---")
    st.markdown("### 關於本工具")
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
    
    model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=sys_instruction)
    
    user_prompt = f"我的目標平台是：{platform}。"
    if resolution:
        user_prompt += f" 請強制輸出解析度為：{resolution}。"
    if extra_instruction:
        user_prompt += f" 額外使用者要求：{extra_instruction}。"
    
    response = model.generate_content([user_prompt, image])
    return response.text

# --- 6. 介面佈局 ---
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("1. 來源與設定")
    uploaded_file = st.file_uploader("上傳原始圖片 (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="原始圖片預覽", use_column_width=True)
        
        with st.container():
            st.markdown("#### 2. 參數配置")
            platform = st.selectbox(
                "目標平台",
                ("TikTok (9:16)", "Instagram (1:1)", "YouTube (16:9)", "小紅書 (3:4)", "Album Cover (1:1)")
            )
            
            resolution = None
            if "Instagram" in platform or "Album Cover" in platform:
                resolution = st.selectbox(
                    "輸出解析度 (1:1 專用)",
                    ("1400x1400", "1600x1600", "1800x1800", "3000x3000 (發行級)")
                )
            
            extra_inst = st.text_area("額外指令 (選填)", placeholder="例如：背景改為賽博龐克風格...")
            generate_btn = st.button("🚀 生成適配指令")

with col2:
    st.subheader("3. 生成結果")
    if uploaded_file and generate_btn:
        if not api_key:
            st.error("❌ 請先配置 API Key")
        else:
            with st.spinner("🤖 AI 正在解構圖片並重新排版..."):
                try:
                    result = get_gemini_response(image, platform, resolution, extra_inst)
                    st.success("生成完成！")
                    tab1, tab2 = st.tabs(["📋 生圖 Prompt", "🔍 完整分析"])
                    with tab1:
                        st.markdown("##### 請複製以下指令：")
                        st.code(result, language="json")
                    with tab2:
                        st.json({"Platform": platform, "Resolution": resolution})
                except Exception as e:
                    st.error(f"錯誤：{str(e)}")
    elif not uploaded_file:
        st.info("👈 請在左側上傳圖片")
