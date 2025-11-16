import requests 

import streamlit as st

st.title("mlops-demo-chat")

## TODO: revert to only show most recent message display history...? test performance later
## TODO: create .env/config pattern
BACKEND_URL = "http://localhost:8000/chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# TODO: metadata show in UI...?
prompt = st.chat_input("Type something")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        payload = {
            "prompt": prompt 
        }
        resp = requests.post(f"{BACKEND_URL}", json=payload)
        st.markdown(resp.json())
        st.session_state.messages.append({"role": "assistant", "content": resp.json()})
