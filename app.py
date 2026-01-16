import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 頁面基礎設定 ---
st.set_page_config(
    page_title="VisualAdapt AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS 樣式美化 ---
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

# --- 3. 側邊欄：API Key 讀取 ---
with st.sidebar:
    st.header("⚙️ 設定")
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ 已自動載入系統 API Key")
    else:
        api_key = st.text_input("Google Gemini API Key", type="password", placeholder="請輸入 API Key")
        if not api_key:
            st.warning("⚠️ 請輸入 Key 才能使用")
            st.markdown("[👉 獲取 API Key](https://aistudio.google.com/app/apikey)")
            
    st.markdown("---")
    st.info("專為創作者設計，自動生成多平台適配指令。")
    # 顯示當前使用的超前版本模型
    st.caption("🔥 Powered by Gemini 2.5 Flash")

# --- 4. 主標題 ---
st.title("🎨 VisualAdapt AI")
st.markdown("### 跨平台縮圖與專輯封面適配器 (Gemini 2.5/3.0 版)")

# --- 5. 介面佈局 ---
col1, col2 = st.columns([1, 1.5], gap="large")

uploaded_file = None
platform = "TikTok (9:16)"
resolution = None
extra_inst = ""
generate_btn = False

with col1:
    st.subheader("1. 來源與設定")
    
    uploaded_file = st.file_uploader("上傳原始圖片 (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="原始圖片預覽", use_column_width=True)
        
        st.markdown("#### 2. 參數配置")
        platform = st.selectbox(
            "目標平台",
            ("TikTok (9:16)", "Instagram (1:1)", "YouTube (16:9)", "小紅書 (3:4)", "Album Cover (1:1)")
        )
        
        if "Instagram" in platform or "Album Cover" in platform:
            resolution = st.selectbox(
                "輸出解析度 (1:1 專用)",
                ("1400x1400", "1600x1600", "1800x1800", "3000x3000 (發行級)")
            )
        
        extra_inst = st.text_area("額外指令 (選填)", placeholder="例如：背景改為賽博龐克風格...")
        generate_btn = st.button("🚀 生成適配指令")

# --- 6. 生成邏輯 (針對您的帳號型號特別定制) ---
with col2:
    st.subheader("3. 生成結果")
    
    if uploaded_file and generate_btn:
        if not api_key:
            st.error("❌ 請先配置 API Key")
        else:
            with st.spinner("🤖 AI 正在使用 Gemini 2.5 Flash 進行分析..."):
                try:
                    genai.configure(api_key=api_key)
                    
                    # 組合提示詞
                    final_prompt = f"Target Platform: {platform}. "
                    if resolution:
                        final_prompt += f"Target Resolution: {resolution}. "
                    if extra_inst:
                        final_prompt += f"User Requirement: {extra_inst}. "
                    
                    sys_prompt = """
                    You are an expert AI art director.
                    Mission: Recompose the image for the target platform.
                    Rules:
                    1. Output specific aspect ratios.
                    2. If changing from Landscape to Portrait, use "Shift and Scale" logic, don't just extend borders.
                    3. Output format must be JSON: { "platform": "...", "prompt": "..." }
                    """
                    
                    # --- 關鍵修改：使用您診斷列表中的第 0 項模型 ---
                    # 您的帳號支援 2.5 Flash，這是目前最新最快的選擇
                    model_name = 'models/gemini-2.5-flash' 
                    
                    try:
                        model = genai.GenerativeModel(model_name, system_instruction=sys_prompt)
                        response = model.generate_content([final_prompt, image])
                    except Exception:
                        # 如果 2.5 Flash 失敗，嘗試您的 3.0 Pro Preview
                        st.warning("嘗試切換至 Gemini 3 Pro Preview...")
                        model_name = 'models/gemini-3-pro-preview'
                        model = genai.GenerativeModel(model_name, system_instruction=sys_prompt)
                        response = model.generate_content([final_prompt, image])

                    # 顯示結果
                    st.success(f"生成完成！(使用模型: {model_name})")
                    
                    tab1, tab2 = st.tabs(["📋 生圖 Prompt", "🔍 完整數據"])
                    with tab1:
                        st.code(response.text, language="json")
                    with tab2:
                        st.json({"Platform": platform, "Resolution": resolution, "Model": model_name})
                        
                except Exception as e:
                    st.error("發生錯誤，請截圖給開發者：")
                    st.error(f"錯誤詳情: {str(e)}")
                    
    elif not uploaded_file:
        st.info("👈 請先在左側上傳一張圖片")
