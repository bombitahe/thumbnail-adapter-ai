import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- 1. 頁面基礎設定 ---
st.set_page_config(page_title="VisualAdapt AI", page_icon="🎨", layout="wide")

# --- 2. CSS 樣式 ---
st.markdown("""
<style>
    .stButton>button { width: 100%; background-color: #4F46E5; color: white; border-radius: 8px; height: 3em; font-weight: bold; }
    .stSelectbox, .stTextInput, .stTextArea { border-radius: 8px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. 側邊欄與 API Key ---
with st.sidebar:
    st.header("⚙️ 設定")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ 系統 Key 已載入")
        # 顯示版本號以供除錯
        st.caption(f"SDK Version: {genai.__version__}") 
    else:
        api_key = st.text_input("Google Gemini API Key", type="password")
        if not api_key:
            st.warning("⚠️ 請輸入 API Key")

    st.markdown("---")
    st.info("自動適配多平台縮圖指令。")

# --- 4. 主標題 ---
st.title("🎨 VisualAdapt AI")

# --- 5. 介面佈局 ---
col1, col2 = st.columns([1, 1.5], gap="large")
uploaded_file = None
platform = "TikTok (9:16)"
resolution = None
extra_inst = ""
generate_btn = False

with col1:
    st.subheader("1. 來源與設定")
    uploaded_file = st.file_uploader("上傳原始圖片", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="預覽", use_column_width=True)
        st.markdown("#### 2. 參數配置")
        platform = st.selectbox("目標平台", ("TikTok (9:16)", "Instagram (1:1)", "YouTube (16:9)", "小紅書 (3:4)", "Album Cover (1:1)"))
        if "Instagram" in platform or "Album Cover" in platform:
            resolution = st.selectbox("解析度", ("1400x1400", "1600x1600", "1800x1800", "3000x3000"))
        extra_inst = st.text_area("額外指令", placeholder="例如：賽博龐克風格...")
        generate_btn = st.button("🚀 生成指令")

# --- 6. 生成邏輯 (三層保險機制) ---
with col2:
    st.subheader("3. 生成結果")
    
    if uploaded_file and generate_btn:
        if not api_key:
            st.error("❌ 無 API Key")
        else:
            with st.spinner("🤖 AI 正在嘗試連接模型..."):
                genai.configure(api_key=api_key)
                
                # 構建 Prompt
                prompt_text = f"Target Platform: {platform}. "
                if resolution: prompt_text += f"Resolution: {resolution}. "
                if extra_inst: prompt_text += f"Extra: {extra_inst}. "
                
                sys_prompt = "You are an AI art director. Recompose image layout for target platform. Output JSON: {platform, prompt}."

                # 定義模型嘗試清單 (從新到舊)
                models_to_try = [
                    'gemini-1.5-flash', # 首選
                    'gemini-1.5-pro',   # 次選
                    'gemini-pro'        # 保底 (1.0版本)
                ]
                
                success = False
                last_error = ""

                for model_name in models_to_try:
                    try:
                        # 嘗試生成
                        model = genai.GenerativeModel(model_name, system_instruction=sys_prompt)
                        # 注意：舊版模型可能不支援 system_instruction，這裡做個簡單兼容
                        if model_name == 'gemini-pro':
                             response = model.generate_content([sys_prompt + "\n" + prompt_text, image])
                        else:
                             response = model.generate_content([prompt_text, image])
                        
                        # 成功了！
                        st.success(f"生成成功！(使用模型: {model_name})")
                        tab1, tab2 = st.tabs(["📋 JSON Result", "🔍 Debug"])
                        with tab1: st.code(response.text, language="json")
                        with tab2: st.json({"Model": model_name, "Platform": platform})
                        success = True
                        break # 跳出迴圈

                    except Exception as e:
                        print(f"嘗試 {model_name} 失敗: {e}")
                        last_error = str(e)
                        time.sleep(1) # 休息一下再試下一個

                if not success:
                    st.error("❌ 所有模型都嘗試失敗。")
                    st.error(f"最後一次錯誤訊息: {last_error}")
                    st.warning("建議：請檢查 API Key 是否有開啟權限，或嘗試重新建立一個新的 Key。")

    elif not uploaded_file:
        st.info("👈 請上傳圖片")
