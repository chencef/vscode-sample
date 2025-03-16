# 產生一個 Streamlit 範例程式

import streamlit as st

# 標題
st.title("Hello, Streamlit!")

# 副標題
st.subheader("這是一個簡單的範例程式")

# 輸入框
name = st.text_input("請輸入你的名字：")

# 按鈕
if st.button("提交"):
    st.write(f"你好, {name}!")