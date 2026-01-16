import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import io
import requests
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
        
    st.markdown("---")
    st.caption("🔥 Mode: Gemini 3 Pro (All-in-One)")

# --- 4. 主界面 ---
st.title("🎨 VisualAdapt AI (Pro)")
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("1. 来源与设置")
    uploaded_file = st.file_uploader("上传图片", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="预览", use_column_width=True)
        
        platform = st.selectbox("目标平台", ("TikTok (9:16)", "Instagram (1:1)", "YouTube (16:9)", "小红书 (3:4)", "Album Cover (1:1)"))
        extra_inst = st.text_area("额外指令", placeholder="例如：背景改为赛博朋克...")
        generate_btn = st.button("🚀 生成图片 (Generate)")

# --- 5. 核心逻辑 (Gemini 3 Pro 原生生图版) ---
with col2:
    st.subheader("3. 生成结果")
    
    if uploaded_file and generate_btn:
        if not api_key:
            st.error("❌ 请先配置 API Key")
        else:
            # 1. 先用 Gemini 2.5 Flash 快速写指令 (为了省钱和速度)
            prompt_text = ""
            with st.spinner("🧠 阶段 1/2：正在构思画面..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('models/gemini-2.5-flash', 
                        system_instruction='Analyze image and output JSON { "prompt": "..." } for regeneration.')
                    user_req = f"Platform: {platform}. User Note: {extra_inst}"
                    response = model.generate_content([user_req, image])
                    
                    clean_text = response.text.replace("```json", "").replace("```", "").strip()
                    prompt_data = json.loads(clean_text)
                    prompt_text = prompt_data.get("prompt", "")
                    st.success("✅ 指令构思完成！")
                    with st.expander("查看咒语"): st.code(prompt_text)
                except Exception as e:
                    st.error(f"文字生成失败: {e}")
                    st.stop()

            # 2. 呼叫 Gemini 3 Pro 直接生图 (REST API)
            if prompt_text:
                with st.spinner("🎨 阶段 2/2：Gemini 3 Pro 正在绘图..."):
                    try:
                        # 👇 关键修改：使用你列表里的 Gemini 3 Pro Image Preview 模型
                        # 注意：Gemini 生图使用的是 generateContent 接口，不是 predict
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key={api_key}"
                        headers = {'Content-Type': 'application/json'}
                        
                        # 转换比例 (Gemini 3 原生支持比例描述，我们在 Prompt 里加强)
                        final_prompt = f"Generate an image of: {prompt_text}. Aspect Ratio: {platform}"

                        payload = {
                            "contents": [{
                                "parts": [{"text": final_prompt}]
                            }]
                        }
                        
                        response = requests.post(url, headers=headers, json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            # 解析 Gemini 的内嵌图片数据
                            try:
                                # Gemini 返回图片通常在 parts 里的 inline_data 或者是 file_uri
                                # 这里尝试解析 inline_data (Base64)
                                img_b64 = None
                                candidates = data.get('candidates', [])
                                if candidates:
                                    parts = candidates[0].get('content', {}).get('parts', [])
                                    for part in parts:
                                        if 'inline_data' in part:
                                            img_b64 = part['inline_data']['data']
                                            break
                                
                                if img_b64:
                                    img_data = base64.b64decode(img_b64)
                                    result_image = Image.open(io.BytesIO(img_data))
                                    st.image(result_image, caption="Gemini 3 Pro 生成结果", use_column_width=True)
                                    
                                    st.download_button(
                                        label="📥 下载图片 (Download PNG)",
                                        data=img_data,
                                        file_name="gemini_gen.png",
                                        mime="image/png"
                                    )
                                else:
                                    # 如果没返回图片，可能是被安全拦截或返回了纯文本
                                    st.warning("⚠️ 生成完成，但未检测到图片数据。可能原因：")
                                    st.json(data) # 打印出来看看
                            except Exception as e:
                                st.error(f"解析图片失败: {e}")
                                st.json(data)
                        else:
                            st.error(f"❌ 请求失败 (Status: {response.status_code})")
                            st.code(response.text)
                            st.caption("如果依然 404，请尝试在代码第 78 行把模型名改为 'gemini-2.0-flash-exp'")

                    except Exception as e:
                        st.error(f"❌ 网络请求错误: {e}")

    elif not uploaded_file:
        st.info("👈 请上传图片")
