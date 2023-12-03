import streamlit as st

with open('output2.html', 'r') as file:
    html_content = file.read()
st.markdown(html_content, unsafe_allow_html=True)