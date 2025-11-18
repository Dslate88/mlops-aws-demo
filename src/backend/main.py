from pydantic import BaseModel
from fastapi import FastAPI
import mlflow
from mlflow.tracking import MlflowClient
from dotenv import load_dotenv
import onnxruntime as rt
import numpy as np

from .baml_client import b
from .baml_client.types import (
    ModelRegistryAPI,
    ModelStageAPI,
    NonApprovedRequest,
    ModelInferenceAPI,
    ModelInput,
)
from .baml_client.types import ModelInput
from ..backend.models.titanic import TitanicModelService


## TODO idea:
# - rollback logic?
# - delete model option?
# - train model option? (model_name, var_list, etc?)

load_dotenv()

MLFLOW_TRACKING_URI = "http://127.0.0.1:5000/"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Default")

client = MlflowClient()

app = FastAPI(title="ML_LLM Ops Demo - Backend APIs", version="0.0.1")


class ChatRequest(BaseModel):
    prompt: str


# ########################################################
# TODO: utility functions find home later
def get_latest_version(model_name):
    versions = client.search_model_versions(f"name='{model_name}'")
    return max([int(x.version) for x in versions])


def get_models():
    models = {}
    for rm in client.search_registered_models():
        latest = get_latest_version(rm.name)
        mv = client.get_model_version(rm.name, latest)
        models[rm.name] = mv.tags.get("app_stage")
    return models


# TODO: metadata that dhows valid options per action to user??
def set_model_stage(model_name, operation):
    version = get_latest_version(model_name)
    target_stage = "Production" if operation == "elevate" else "Archived"
    current_stage = client.get_model_version(model_name, version).tags.get("app_stage")

    if current_stage != target_stage:
        client.set_model_version_tag(
            name=model_name, version=version, key="app_stage", value=target_stage
        )
        return f"`{model_name}` sucessfully set to `{target_stage}`."
    else:
        return f"No action taken. `{model_name}` already set to `{target_stage}`."


def render_markdown(models):
    lines = ["**Models:**"]
    for name, stage in models.items():
        lines.append(f"- `{name}` (stage: `{stage}`)")
    return "\n".join(lines)


# ########################################################


@app.get("/")
def home():
    return {"message": "Hello!"}


# TODO: setup multi-model prediction pattern
def predict(sex, pclass, embarked, alone):
    MODEL_NAME = "titanic"

    onnx_model = mlflow.onnx.load_model(f"models:/{MODEL_NAME}/latest")
    sess = rt.InferenceSession(onnx_model.SerializeToString())

    feed = {
        "sex": np.array([[sex]], dtype=object),
        "pclass": np.array([[pclass]], dtype=np.int64),
        "embarked": np.array([[embarked]], dtype=object),
        "alone": np.array([[alone]], dtype=np.int64),
    }
    output = sess.run(None, feed)

    pred = int(output[0].item())
    pred

    return {"message": pred}


@app.post("/chat")
def chat(request: ChatRequest):
    MODELS = get_models()
    resp = b.SelectTool(request.prompt)

    # TODO: will handle intent responses later...
    if isinstance(resp, ModelRegistryAPI):
        return {"content": render_markdown(MODELS)}

    if isinstance(resp, ModelStageAPI):
        if resp.model_name in MODELS.keys():
            result = set_model_stage(resp.model_name, resp.operation)
            return {"content": result}
        else:
            return {
                "content": f"You requested an invalid model. Choose from\n{render_markdown(MODELS)}"
            }

    if isinstance(resp, ModelInferenceAPI):
        svc = TitanicModelService()
        mi: ModelInput = b.ValidateInput(request.prompt)

        if mi.missing_details:
            incomplete_response = svc.missing_response(mi.missing_details)
            return {
                "content": incomplete_response,
                "metadata": {
                    "valid_values": svc.valid_values(),
                },
            }

        features = svc.transform(mi)
        raw_pred = svc.predict(features)
        content = svc.format_response(raw_pred)

        return {
            "content": content,
            "metadata": {
                "raw_prediction": raw_pred,
                "model_name": svc.model_name,
                "valid_values": svc.valid_values(),
            },
        }

    # TODO: inject list of approved actions
    if isinstance(resp, NonApprovedRequest):
        result = (
            "This is not an approved request. You may ask about <insert_list> later.."
        )
        return {"content": result}

    # TODO: add help intent handling?
