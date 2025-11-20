import requests

import streamlit as st

st.title("mlops-demo-chat")

## TODO: revert to only show most recent message display history...? test performance later
## TODO: create .env/config pattern
# TODO: add info that informs users of 'rules' of the app. ex: only 1 prod model at a time.
BACKEND_URL = "http://localhost:8000/chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2, col3, col4 = st.columns(4)
help_prompt = None
if col1.button("List models"):
    help_prompt = "What models are available?"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = help_prompt or st.chat_input("Type something")

# TODO: display proba instead...
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        payload = {"prompt": prompt}
        resp = requests.post(f"{BACKEND_URL}", json=payload).json()

        content = resp.get("content")
        kind = resp.get("kind")
        is_error = resp.get("error")

        if is_error:
            st.error(resp.get("content"))
        else:
            st.markdown(resp.get("content"))

        if kind == "list_models":
            st.caption("Tip: try `Elevate <model_name> to production` next.")

        if resp.get("metadata"):
            with st.expander("Show metadata", expanded=False):
                st.json(resp.get("metadata"))

        st.session_state.messages.append({"role": "assistant", "content": content})
