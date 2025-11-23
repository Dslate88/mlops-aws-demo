import os
import requests

import streamlit as st

st.title("mlops-demo-chat")

# TODO: have a header/banner showing the active prod model + version?

## TODO: ensure users know that history is displayed, but only last message is submitted each time.
## TODO: create .env/config pattern
# TODO: add info that informs users of 'rules' of the app. ex: only 1 prod model at a time.
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# session_state initialize
if "messages" not in st.session_state:
    st.session_state.messages = []

if "help_prompt" not in st.session_state:
    st.session_state.help_prompt = None

# helper prompt buttons
col1, col2, col3, col4 = st.columns(4)
if col1.button("List models"):
    st.session_state.help_prompt = "What models are available?"
if col2.button("Elevate model"):
    st.session_state.help_prompt = "Elevate titanic to production."
if col3.button("Train model"):
    st.session_state.help_prompt = "Train titanic model with test size of .3"
if col4.button("Test Model"):
    st.session_state.help_prompt = "Test model"

# display messages upon rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# handle user_input
# note: two needed because streamlit rerun design...doesnt have VDOM like react...
user_input = st.chat_input("Type something")
prompt = st.session_state.help_prompt or user_input
st.session_state.help_prompt = None


def render_active_model_banner():
    try:
        resp = requests.get(f"{BACKEND_URL}/active-model", timeout=10)
        data = resp.json()
    except Exception:
        st.warning("No production model currently active.")
        return

    active_model = data.get("name")
    active_version = data.get("version")

    if active_model:
        st.success(
            f"Active production model: `{data.get('name')}` version: `{active_version}`"
        )
    else:
        st.info(
            "No model is currently in Production. Train and elevate a model to get started."
        )
        st.info(data)


render_active_model_banner()


# special handlers based on ChatResponse.kind
def handle_list_models(resp, is_error):
    if not is_error:
        st.caption("Tip: try `Elevate <model_name> to production` next.")


def handle_elevate(resp, is_error):
    if not is_error:
        st.caption("Tip: You can now test model by saying `I want to test the model`.")


def handle_missing_inputs(resp, is_error):
    valid_values = resp.get("metadata", {}).get("valid_values", {})
    if valid_values:
        with st.expander("Valid values", expanded=False):
            for field, values in valid_values.items():
                st.write(f"**{field}**: {', '.join(values)}")


def handle_inference(resp, is_error):
    meta = resp.get("metadata", {})
    raw = meta.get("raw_prediction")
    model_name = meta.get("model_name")
    if raw is not None and model_name:
        st.caption(f"{model_name} raw prediction: `{raw}`")


def handle_train(resp, is_error):
    # TODO: add more later
    st.caption(f"Tip: try to test this model now!, or elevate")
    meta = resp.get("metadata", {})
    results = meta.get("train_results")
    if results is not None:
        with st.expander("train metadata", expanded=False):
            for field, values in results.items():
                st.write(f"**{field}**: `{str(values)}`")


KIND_HANDLERS = {
    "list_models": handle_list_models,
    "elevate": handle_elevate,
    "missing_inputs": handle_missing_inputs,
    "inference": handle_inference,
    "train": handle_train,
}


# TODO: display proba instead...
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        # hit baml layer for intent routing
        payload = {"prompt": prompt}
        resp = requests.post(f"{BACKEND_URL}/chat", json=payload).json()

        # parse response
        content = resp.get("content")
        kind = resp.get("kind")
        is_error = resp.get("error")

        # conditionally display content
        if is_error:
            st.error(resp.get("content"))
        else:
            st.markdown(resp.get("content"))

        # handle extras associated with ChatResponse.kind
        handler = KIND_HANDLERS.get(kind)
        if handler:
            handler(resp, is_error)

        st.session_state.messages.append({"role": "assistant", "content": content})
