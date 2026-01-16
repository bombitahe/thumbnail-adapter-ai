import streamlit as st
import google.generativeai as genai
import os

# 修正點：將 icon 改為 page_icon
st.set_page_config(page_title="API 診斷", page_icon="🛠️")
st.title("🛠️ API 連線診斷模式")

# 1. 檢查鑰匙是否存在
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    # 顯示鑰匙的前 5 碼，讓你確認
    if api_key:
        st.info(f"🔑 正在測試的 API Key 開頭是：{api_key[:5]}...")
    else:
        st.error("❌ Secrets 裡有 GOOGLE_API_KEY 欄位，但是是空的！")
else:
    st.error("❌ 程式完全沒讀到 Secret 裡的 Key！請檢查 Secrets 格式。")

# 2. 測試連線
if api_key:
    genai.configure(api_key=api_key)
    
    st.write("📡 正在嘗試連線 Google...")
    
    try:
        # 列出所有模型
        model_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        
        if model_list:
            st.success(f"✅ **連線成功！** 您的 Key 是有效的！")
            st.write(f"您的帳號可以使用以下模型：")
            st.json(model_list)
            st.markdown("---")
            
            # 自動檢查是否有 Flash 模型
            if 'models/gemini-1.5-flash' in model_list:
                st.success("🎉 恭喜！您的帳號支援 `gemini-1.5-flash`！我們之前的代碼可以直接用！")
            else:
                st.warning("⚠️ 注意：您的帳號裡沒有 Flash 模型，但有其他的。請把上面的列表截圖給我，我幫您改代碼。")
                
        else:
            st.warning("⚠️ 連線成功，但回傳了「空列表」。這代表 API Key 有效，但該專案沒有啟用 Generative Language API。")
            st.markdown("[👉 點此前往 Google Cloud Console 啟用 API](https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com)")
            
    except Exception as e:
        st.error("❌ **連線失敗**")
        st.error(f"錯誤訊息：{str(e)}")
        st.markdown("""
        **常見原因：**
        1. API Key 貼錯了（多了空格？）。
        2. Google Cloud 專案權限被凍結。
        3. 區域限制（極少數情況）。
        """)
