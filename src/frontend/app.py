import os
import requests

import streamlit as st

APP_TAGLINE = (
    "llm intent router + fastapi modlel hosting + streamlit + mlflow + aws + some mlops"
)

APP_RULES_MD = """
### How this demo works

- **One production model at a time**  
  The backend enforces that only a single model can be in the `Production` stage.  
  Elevating one model will archive any other production models.
  This is done strictly for interactive demo purposes.

- **Prompt examples**  
  The buttons in the sidebar just pre-fill example prompts.  
  It's **recommended** to type your own natural language instructions and experiment.

- **Chat history vs. what gets sent**  
  The full history is displayed for context, but on each turn only your **latest message**
  is sent to the backend.

- **Typical flow**  
  1. Ask: `What models are available?`  
  2. Optionally: `Train titanic model with test size 0.3`  
  3. Elevate: `Elevate titanic to production`  
  4. Then: `I want to test the model in production: I'm a male who had a 2nd class ticket and I departed out of england with my family.`, or something like that..

- **Diclaimer**  
  The focus is to showcase a variety of skillsets, not production-grade reliability.
  For example, a simple thread locking solution was implemented to avoid race conditions...would need refactoring if this were to scale.
"""

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


st.set_page_config(page_title="mlops-demo-chat", layout="wide")
st.title("mlops-demo-chat")


# session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "help_prompt" not in st.session_state:
    st.session_state.help_prompt = None


# helpers
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
            f"Active production model: `{active_model}` (version `{active_version}`)"
        )
    else:
        st.info(
            "No model is currently in Production. Train and elevate a model to get started."
        )
        st.info(data)


def handle_list_models(resp, is_error):
    if not is_error:
        st.caption("Tip: try `Elevate <model_name> to production` next.")

def handle_elevate(resp, is_error):
    if not is_error:
        st.caption("Tip: only one model can be in Production at a time. ")
        st.rerun()


# TODO: add reasoning to inform why it couldnt validate
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
    raw_features = meta.get("raw_features")
    tranformed_features = meta.get("transformed_features")

    reasoning = raw_features.get("reasoning")

    if raw is not None and model_name:
        st.caption(f"{model_name} raw prediction: `{raw}`")
        st.caption(f"What the LLM thought: {str(reasoning)}")
        if raw_features:
            with st.expander("llm guessed these raw values", expanded=False):
                for field, values in raw_features.items():
                    st.write(f"**{field}**: `{str(values)}`")
        if tranformed_features:
            with st.expander("tranformed features prior to inference", expanded=False):
                for field, values in tranformed_features.items():
                    st.write(f"**{field}**: `{str(values)}`")


def handle_train(resp, is_error):
    st.caption("Tip: try testing this model now, or elevating it to Production.")
    if not is_error:
        st.rerun()

    meta = resp.get("metadata", {})
    results = meta.get("train_results")
    if results is not None:
        with st.expander("Train metadata", expanded=False):
            for field, values in results.items():
                st.write(f"**{field}**: `{str(values)}`")


KIND_HANDLERS = {
    "list_models": handle_list_models,
    "elevate": handle_elevate,
    "missing_inputs": handle_missing_inputs,
    "inference": handle_inference,
    "train": handle_train,
}


# pages
def render_demo_guide_page():
    st.caption(APP_TAGLINE)
    st.markdown(APP_RULES_MD)


def render_chat_page():
    with st.sidebar:
        st.subheader("Prefill prompts")

        if st.button("List models"):
            st.session_state.help_prompt = "What models are available?"

        if st.button("Remove model"):
            st.session_state.help_prompt = "Remove titanic model"

        if st.button("Elevate model"):
            st.session_state.help_prompt = "Elevate titanic to production."

        if st.button("Train model"):
            st.session_state.help_prompt = "Train titanic model with test size of .3"

        if st.button("Test titanic model"):
            resp = requests.get(f"{BACKEND_URL}/active-model", timeout=10).json()
            active_model_name = resp.get("name")

            if active_model_name != "titanic":
                st.warning(
                    "The `titanic` model is not currently in Production. "
                    "You may need to train and or elevate it first."
                )
            else:
                st.session_state.help_prompt = (
                    "I want to test the model in production: I'm a 33 year old male who had a 2nd class ticket "
                    "and I departed out of england."
                )

    render_active_model_banner()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Type something")
    prompt = st.session_state.help_prompt or user_input
    st.session_state.help_prompt = None

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            payload = {"prompt": prompt}
            resp = requests.post(f"{BACKEND_URL}/chat", json=payload).json()

            content = resp.get("content")
            kind = resp.get("kind")
            is_error = resp.get("error")

            if is_error:
                st.error(content)
            else:
                st.markdown(content)

            handler = KIND_HANDLERS.get(kind)
            if handler:
                handler(resp, is_error)

        st.session_state.messages.append({"role": "assistant", "content": content})


# main
with st.sidebar:
    st.title("Navigation")
    page = st.radio("Go to", ["Chat", "Demo guide"])
    st.markdown("---")
    st.markdown("https://github.com/Dslate88/mlops-aws-demo")

if page == "Demo guide":
    render_demo_guide_page()
else:
    render_chat_page()
