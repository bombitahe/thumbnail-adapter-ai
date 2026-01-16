import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import io

# --- 1. 頁面基礎設定 ---
st.set_page_config(
    page_title="VisualAdapt AI (Pro)",
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
    /* 隱藏多餘元素 */
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
    st.info("專為創作者設計，支援文字分析與圖像生成。")
    st.caption("🔥 Powered by Gemini 2.5 & Imagen 3")

# --- 4. 主標題 ---
st.title("🎨 VisualAdapt AI (Pro)")
st.markdown("### 跨平台縮圖與專輯封面生成器")

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
        
        # 解析度只影響 Prompt 的描述，生圖模型通常有固定比例
        if "Instagram" in platform or "Album Cover" in platform:
            resolution = st.selectbox(
                "輸出解析度 (1:1 專用)",
                ("1400x1400", "1600x1600", "1800x1800", "3000x3000 (發行級)")
            )
        
        extra_inst = st.text_area("額外指令 (選填)", placeholder="例如：背景改為賽博龐克風格...")
        generate_btn = st.button("🚀 生成圖片 (Generate Image)")

# --- 6. 雙重生成邏輯 (大腦+畫家) ---
with col2:
    st.subheader("3. 生成結果")
    
    if uploaded_file and generate_btn:
        if not api_key:
            st.error("❌ 請先配置 API Key")
        else:
            # 設定 Key
            genai.configure(api_key=api_key)

            # --- 階段一：Gemini 大腦思考 (寫 Prompt) ---
            prompt_text = ""
            with st.spinner("🧠 階段 1/2：Gemini 正在分析構圖並撰寫繪圖指令..."):
                try:
                    # 使用您帳號中可用的 Gemini 模型
                    # 優先嘗試 2.5 Flash
                    model_name_llm = 'models/gemini-2.5-flash'
                    
                    sys_prompt = """
                    You are an expert AI art director.
                    Mission: Analyze the uploaded image and write a detailed text prompt to RE-GENERATE this image for a new aspect ratio.
                    Rules:
                    1. Describe the main subject, style, lighting, and colors in detail.
                    2. Adjust the description to fit the target platform's aspect ratio (e.g., extend background for vertical).
                    3. Output Format: ONLY pure JSON string. { "prompt": "..." }
                    """
                    
                    user_content = f"Target Platform: {platform}. Resolution: {resolution}. User Note: {extra_inst}"
                    
                    try:
                        model = genai.GenerativeModel(model_name_llm, system_instruction=sys_prompt)
                        response = model.generate_content([user_content, image])
                    except:
                        # 備用：如果 2.5 失敗，用 1.5 Pro
                        model = genai.GenerativeModel('models/gemini-1.5-pro', system_instruction=sys_prompt)
                        response = model.generate_content([user_content, image])

                    # 清理 JSON
                    clean_json = response.text.replace("```json", "").replace("```", "").strip()
                    prompt_data = json.loads(clean_json)
                    prompt_text = prompt_data.get("prompt", "")
                    
                    st.success("✅ 指令撰寫完成！")
                    with st.expander("查看生成的英文咒語 (Prompt)"):
                        st.code(prompt_text)

                except Exception as e:
                    st.error(f"❌ 階段一失敗 (文字生成)：{e}")
                    st.stop()

            # --- 階段二：Imagen 畫家作畫 (生成圖片) ---
            if prompt_text:
                with st.spinner("🎨 階段 2/2：Imagen 3 正在繪製圖片 (這需要一點時間)..."):
                    try:
                        # 使用 Imagen 3 模型
                        # 注意：這是 Google Cloud 標準付費模型的名稱
                        imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                        
                        # 設定比例 (根據平台選擇)
                        ar = "1:1"
                        if "9:16" in platform: ar = "9:16"
                        elif "16:9" in platform: ar = "16:9"
                        elif "3:4" in platform: ar = "3:4"
                        
                        # 開始生圖
                        result = imagen_model.generate_images(
                            prompt=prompt_text,
                            number_of_images=1,
                            aspect_ratio=ar,
                            safety_filter_level="block_only_high",
                            person_generation="allow_adult"
                        )
                        
                        # 顯示圖片
                        generated_image = result.images[0]
                        st.image(generated_image, caption=f"生成結果 ({platform})", use_column_width=True)
                        
                        # --- 下載按鈕 ---
                        # 將圖片轉換為字節流以便下載
                        img_byte_arr = io.BytesIO()
                        generated_image.save(img_byte_arr, format='PNG')
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        st.download_button(
                            label="📥 下載圖片 (Download PNG)",
                            data=img_byte_arr,
                            file_name="generated_cover.png",
                            mime="image/png"
                        )
                        
                    except Exception as e:
                        st.error("❌ 階段二失敗 (圖片生成)：")
                        st.warning(f"您的 API Key 可能沒有 Imagen 3 的存取權限，或者該模型名稱在您的區域尚未開放。\n錯誤訊息：{e}")
                        st.info("💡 建議：您可以複製上面的英文咒語，去 Midjourney 生成。")

    elif not uploaded_file:
        st.info("👈 請先在左側上傳一張圖片")
