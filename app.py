import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import io
import requests
import base64

# --- 1. 页面设定 ---
st.set_page_config(page_title="VisualAdapt AI (Final)", page_icon="🎨", layout="wide")

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
    # 👇 这里的标题改了，让你知道现在用的是 2.0 Exp
    st.caption("🔥 Mode: Gemini 2.0 Flash Exp (Unlimited)")

# --- 4. 主界面 ---
st.title("🎨 VisualAdapt AI (Final)")
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

# --- 5. 核心逻辑 ---
with col2:
    st.subheader("3. 生成结果")
    
    if uploaded_file and generate_btn:
        if not api_key:
            st.error("❌ 请先配置 API Key")
        else:
            # 1. 构思画面 (SDK)
            prompt_text = ""
            with st.spinner("🧠 阶段 1/2：正在构思画面..."):
                try:
                    # 使用 2.0 Flash Exp 来做文字分析（这个模型很聪明）
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('models/gemini-2.0-flash-exp', 
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

            # 2. 生成图片 (REST API - 2.0 Flash Exp)
            if prompt_text:
                with st.spinner("🎨 阶段 2/2：Gemini 2.0 Flash 正在绘图..."):
                    try:
                        # 👇 关键修改：换成了 'gemini-2.0-flash-exp'
                        # 这个模型是目前唯一开放给大众 API 且支持生图的稳定版
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
                        headers = {'Content-Type': 'application/json'}
                        
                        final_prompt = f"Generate a high quality image of: {prompt_text}. Aspect Ratio: {platform}"

                        payload = {
                            "contents": [{
                                "parts": [{"text": final_prompt}]
                            }],
                            "generationConfig": {
                                "responseMimeType": "image/jpeg" 
                            }
                        }
                        
                        response = requests.post(url, headers=headers, json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            img_b64 = None
                            try:
                                candidates = data.get('candidates', [])
                                if candidates:
                                    parts = candidates[0].get('content', {}).get('parts', [])
                                    for part in parts:
                                        # 2.0 的返回格式可能包含 inline_data
                                        if 'inline_data' in part:
                                            img_b64 = part['inline_data']['data']
                                            break
                                
                                if img_b64:
                                    img_data = base64.b64decode(img_b64)
                                    result_image = Image.open(io.BytesIO(img_data))
                                    st.image(result_image, caption="Gemini 2.0 生成结果", use_column_width=True)
                                    
                                    st.download_button(
                                        label="📥 下载图片 (Download PNG)",
                                        data=img_data,
                                        file_name="gemini_2_gen.png",
                                        mime="image/png"
                                    )
                                else:
                                    st.warning("⚠️ 收到回应但无图片，可能是模型认为内容不安全。")
                                    # 打印出来看看
                                    st.json(data)
                            except Exception as e:
                                st.error(f"解析失败: {e}")
                        
                        elif response.status_code == 429:
                            st.error("❌ 依然显示配额不足")
                            st.info("这说明您的 API Key 所在的项目被 Google 全局限流了。建议：去 Google AI Studio 重新申请一个全新的 Key (New Project)，不要用旧项目的 Key。")
                        else:
                            st.error(f"❌ 请求失败 (Status: {response.status_code})")
                            st.code(response.text)

                    except Exception as e:
                        st.error(f"❌ 网络请求错误: {e}")

    elif not uploaded_file:
        st.info("👈 请上传图片")
