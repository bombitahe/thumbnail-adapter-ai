import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import io
import requests # 👈 新主角：网络请求库
import base64

# --- 1. 页面设定 ---
st.set_page_config(page_title="VisualAdapt AI (Pro)", page_icon="🎨", layout="wide")

# --- 2. 样式美化 ---
st.markdown("""
<style>
    .stButton>button { width: 100%; background-color: #4F46E5; color: white; border-radius: 8px; height: 3em; font-weight: bold; }
    .stSelectbox, .stTextInput, .stTextArea { border-radius: 8px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. API Key 读取 ---
with st.sidebar:
    st.header("⚙️ 设置")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API Key 已载入")
    else:
        api_key = st.text_input("Google Gemini API Key", type="password")
        if not api_key:
            st.warning("⚠️ 请输入 Key")
    
    st.markdown("---")
    st.caption("🔥 Mode: Gemini 2.5 (Brain) + REST API (Painter)")

# --- 4. 主界面 ---
st.title("🎨 VisualAdapt AI (Pro)")
st.markdown("### 跨平台缩图与专辑封面生成器")

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("1. 来源与设置")
    uploaded_file = st.file_uploader("上传图片", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="预览", use_column_width=True)
        
        platform = st.selectbox("目标平台", ("TikTok (9:16)", "Instagram (1:1)", "YouTube (16:9)", "小红书 (3:4)", "Album Cover (1:1)"))
        resolution = None
        if "Instagram" in platform or "Album Cover" in platform:
            resolution = st.selectbox("解析度", ("1400x1400", "3000x3000"))
        
        extra_inst = st.text_area("额外指令", placeholder="例如：背景改为赛博朋克...")
        generate_btn = st.button("🚀 生成图片 (Generate)")

# --- 5. 核心逻辑 (混合动力版) ---
with col2:
    st.subheader("3. 生成结果")
    
    if uploaded_file and generate_btn:
        if not api_key:
            st.error("❌ 请先配置 API Key")
        else:
            # 1. 设定 Gemini
            genai.configure(api_key=api_key)
            prompt_text = ""

            # --- 阶段一：用 SDK 呼叫 Gemini 写指令 (这部分之前是好的) ---
            with st.spinner("🧠 阶段 1/2：Gemini 2.5 正在构思画面..."):
                try:
                    model = genai.GenerativeModel('models/gemini-2.5-flash', 
                        system_instruction='You are an AI art director. Analyze image and output JSON { "prompt": "..." } describing it for regeneration.')
                    
                    user_req = f"Platform: {platform}. User Note: {extra_inst}"
                    response = model.generate_content([user_req, image])
                    
                    # 清理 JSON
                    clean_text = response.text.replace("```json", "").replace("```", "").strip()
                    prompt_data = json.loads(clean_text)
                    prompt_text = prompt_data.get("prompt", "")
                    
                    st.success("✅ 指令构思完成！")
                    with st.expander("查看咒语"): st.code(prompt_text)
                    
                except Exception as e:
                    st.error(f"文字生成失败: {e}")
                    st.stop()

            # --- 阶段二：用 REST API 直连 Google 画图 (绕过 SDK 问题) ---
            if prompt_text:
                with st.spinner("🎨 阶段 2/2：正在呼叫 Imagen 3 作画..."):
                    try:
                        # 准备 API 参数
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={api_key}"
                        headers = {'Content-Type': 'application/json'}
                        
                        # 转换比例
                        ar = "1:1"
                        if "9:16" in platform: ar = "9:16"
                        elif "16:9" in platform: ar = "16:9"
                        elif "3:4" in platform: ar = "3:4"

                        # 发送请求
                        payload = {
                            "instances": [{"prompt": prompt_text}],
                            "parameters": {"sampleCount": 1, "aspectRatio": ar}
                        }
                        
                        # ⚡ 关键一击：直接发 HTTP 请求
                        response = requests.post(url, headers=headers, json=payload)
                        
                        if response.status_code == 200:
                            # 解析图片
                            response_json = response.json()
                            b64_image = response_json['predictions'][0]['bytesBase64Encoded']
                            img_data = base64.b64decode(b64_image)
                            result_image = Image.open(io.BytesIO(img_data))
                            
                            st.image(result_image, caption="生成结果", use_column_width=True)
                            
                            # 下载按钮
                            st.download_button(
                                label="📥 下载图片 (Download PNG)",
                                data=img_data,
                                file_name="generated.png",
                                mime="image/png"
                            )
                        else:
                            # 如果 Google 拒绝了请求 (比如 API Key 没权限)
                            st.error(f"❌ 图片生成请求被拒绝 (Status: {response.status_code})")
                            st.code(response.text)
                            st.info("💡 如果看到 404 或 403，代表您的 API Key 暂时无法存取 Imagen 3 模型。请直接复制上方的 Prompt 去 Midjourney 使用。")

                    except Exception as e:
                        st.error(f"❌ 网络请求错误: {e}")

    elif not uploaded_file:
        st.info("👈 请上传图片")
