import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="API 終極診斷", icon="🛠️")
st.title("🛠️ API 連線診斷模式")

# 1. 檢查鑰匙是否存在
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    # 顯示鑰匙的前 5 碼，讓你確認程式讀到的是不是你新申請的那一把
    st.info(f"🔑 正在測試的 API Key 開頭是：{api_key[:5]}...")
else:
    st.error("❌ 程式完全沒讀到 Secret 裡的 Key！請檢查 Secrets 格式。")

# 2. 測試連線
if api_key:
    genai.configure(api_key=api_key)
    
    st.write("📡 正在嘗試向 Google 伺服器發送 `list_models()` 請求...")
    
    try:
        # 這是最基礎的請求，不涉及任何生圖，只問「你有什麼模型？」
        model_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        
        if model_list:
            st.success(f"✅ **連線成功！** 您的 Key 是有效的！")
            st.write(f"您的帳號目前可以使用以下 {len(model_list)} 個模型：")
            st.json(model_list)
            st.markdown("### 🎉 結論：")
            st.markdown("如果這裡有顯示模型（例如 `models/gemini-pro`），代表**您的 Key 100% 沒問題**，是我們之前的代碼裡模型名稱寫錯了（可能寫成了您帳號沒有的 1.5 版本）。")
        else:
            st.warning("⚠️ 連線成功，但您的帳號裡「沒有任何可用模型」。這通常代表 API 權限未開通。")
            
    except Exception as e:
        st.error("❌ **連線失敗 (Fatal Error)**")
        st.code(str(e))
        st.markdown("### 💀 診斷結論：")
        st.markdown("""
        如果出現 `404` 或 `PermissionDenied`，代表這把 Key **對應的專案設定有誤**。
        
        **極大可能的原因：**
        您在 Google Cloud 啟用的是 **Vertex AI API**，而不是我們需要的 **Generative Language API**。這兩個名字很像，但完全不同！
        """)
