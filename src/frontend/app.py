import requests

import streamlit as st

st.title("mlops-demo-chat")

## TODO: revert to only show most recent message display history...? test performance later
## TODO: create .env/config pattern
# TODO: add info that informs users of 'rules' of the app. ex: only 1 prod model at a time.
BACKEND_URL = "http://localhost:8000/chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "help_prompt" not in st.session_state:
    st.session_state.help_prompt = None

col1, col2, col3, col4 = st.columns(4)
if col1.button("List models"):
    st.session_state.help_prompt = "What models are available?"
if col2.button("Elevate model"):
    st.session_state.help_prompt = "Elevate titanic to production."
if col3.button("Test Model"):
    st.session_state.help_prompt = "Test model"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type something")
prompt = st.session_state.help_prompt or user_input
st.session_state.help_prompt = None

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

        if kind == "elevate" and not is_error:
            # TODO: need to handle this flow in the UI..its missing a step
            st.caption("Tip: You can now test model by saying `I want to test the model`.")

        if kind == "missing_inputs":
            valid_values = resp["metadata"].get("valid_values", {})
            with st.expander("Valid values", expanded=False):
                for field, values in valid_values.items():
                    st.write(f"**{field}**: {', '.join(values)}")

        if kind == "inference":
            raw = resp["metadata"].get("raw_prediction")
            model_name = resp["metadata"].get("model_name")
            st.caption(f"{model_name} raw prediction: `{raw}`")

        st.session_state.messages.append({"role": "assistant", "content": content})
