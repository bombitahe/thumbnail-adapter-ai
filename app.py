import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 設定頁面 ---
st.set_page_config(page_title="AI 全平台縮圖適配器", layout="wide")

# --- 側邊欄：設定 API Key ---
st.sidebar.header("設定")
api_key = st.sidebar.text_input("輸入你的 Google Gemini API Key", type="password")

# --- 主標題 ---
st.title("🎨 YouTube 縮圖全平台適配 App")
st.markdown("上傳一張圖片，自動生成適配 TikTok, IG, 小紅書的排版指令與參數。")

# --- 核心邏輯 ---
def get_gemini_response(image, platform, resolution=None):
    if not api_key:
        return "⚠️ 請先在左側輸入 API Key"
    
    genai.configure(api_key=api_key)
    
    # 這裡放入你精心設計的 System Prompt
    sys_instruction = """
    你是一位精通「跨平台視覺重構」的 AI 技術總監。
    (此處省略部分重複內容，為了節省長度，請把你剛剛在 AI Studio 寫好的那一大段【最終完整版 System Instructions】完整複製貼上覆蓋這裡！)
    """
    
    model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=sys_instruction)
    
    # 建構使用者請求
    user_prompt = f"我的目標平台是：{platform}。"
    if resolution:
        user_prompt += f" 請使用解析度：{resolution}。"
    
    response = model.generate_content([user_prompt, image])
    return response.text

# --- 介面操作 ---
uploaded_file = st.file_uploader("上傳原始縮圖 (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="原始圖片", width=400)

    # 選擇平台
    platform = st.selectbox(
        "選擇目標平台",
        ("TikTok (9:16)", "Instagram (1:1)", "YouTube (16:9)", "小紅書 (3:4)")
    )

    # 1:1 特殊邏輯
    resolution = None
    if "Instagram" in platform:
        resolution = st.selectbox(
            "選擇輸出解析度 (1:1 專用)",
            ("1400x1400", "1600x1600", "1800x1800", "3000x3000 (發行級)")
        )

    if st.button("🚀 開始生成適配指令"):
        with st.spinner("AI 正在分析圖片結構並重構排版..."):
            result = get_gemini_response(image, platform, resolution)
            st.success("生成完成！請查看下方的指令：")
            st.markdown("### 📋 給生圖模型的 Prompt 指令")
            st.code(result, language="json")
            st.info("💡 提示：複製上面的內容到你的生圖工具（如 Midjourney 或 Stable Diffusion）即可。")