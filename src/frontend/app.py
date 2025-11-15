import requests 

import streamlit as st

st.title("Simple chat")

## TODO: create .env/config pattern
BACKEND_URL = "http://localhost:8000/"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type something"):
    resp = requests.get(f"{BACKEND_URL}")
    with st.chat_message("user"):
        st.markdown(resp.json())
    st.session_state.messages.append({"role": "user", "content": prompt})
