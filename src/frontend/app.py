import requests 

import streamlit as st

st.title("Simple chat")

## TODO: make ui display history...
## TODO: create .env/config pattern
BACKEND_URL = "http://localhost:8000/chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# TODO: metadata show in UI...?
if prompt := st.chat_input("Type something"):
    payload = {
        "prompt": prompt 
    }
    resp = requests.post(f"{BACKEND_URL}", json=payload)
    with st.chat_message("user"):
        st.markdown(resp.json())
    st.session_state.messages.append({"role": "user", "content": prompt})
