import os
from pydantic import BaseModel
from fastapi import FastAPI
import mlflow
from mlflow.tracking import MlflowClient
from dotenv import load_dotenv
import onnxruntime as rt
import numpy as np
from typing import Optional, Literal
from threading import Lock

from .baml_client import b
from .baml_client.types import (
    ModelRegistryAPI,
    ModelStageAPI,
    NonApprovedRequest,
    ModelInferenceAPI,
    ModelTrainAPI,
    ModelRemoveAPI,
)
from .models.registry import ModelRegistry
from .models.factory import ModelFactory

## TODO idea:
# - rollback logic?
# - delete model option?
# - train model option? (model_name, var_list, etc?)

load_dotenv()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000/")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Default")

client = MlflowClient()
mr = ModelRegistry(client)

app = FastAPI(title="ML_LLM Ops Demo - Backend APIs", version="0.0.1")

lock = Lock()


class ChatRequest(BaseModel):
    prompt: str


# TODO: keep elevate as only action, remove ability to archive in baml layer...
class ChatResponse(BaseModel):
    content: str
    kind: Literal[
        "list_models",
        "remove_model",
        "elevate",
        "missing_inputs",
        "train",
        "inference",
        "error",
    ]
    error: bool = False
    metadata: Optional[dict] = None


class ActiveModelResponse(BaseModel):
    name: str
    version: int


# TODO: move me
def render_markdown(models):
    lines = ["**Models:**"]
    for name, stage in models.items():
        lines.append(f"- `{name}` (stage: `{stage}`)")
    return "\n".join(lines)


# ########################################################


@app.get("/")
def home():
    return {"message": "Hello!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/active-model")
def active_model():
    active_model = mr.get_production_model()
    version = mr._latest_version(active_model)
    return ActiveModelResponse(
        name=active_model,
        version=version,
    )


@app.post("/chat")
def chat(request: ChatRequest):
    MODELS = mr.list_models()
    active_model = mr.get_production_model()
    resp = b.SelectTool(request.prompt)

    # List Registry Models
    # TODO: if there are no models, handle that with a tip encouraging a train
    if isinstance(resp, ModelRegistryAPI):
        with lock:
            return ChatResponse(
                content=render_markdown(MODELS),
                kind="list_models",
            )

    # Remove model from registry
    if isinstance(resp, ModelRemoveAPI):
        with lock:
            mr.remove_model(resp.model_name)
            return ChatResponse(
                content="sucessfully removed {resp.model_name} from MLFlow Registry.",
                kind="remove_model",
            )

    # Elevate/Archive Models
    if isinstance(resp, ModelStageAPI):
        with lock:
            if resp.model_name in mr:
                result = mr.set_model_stage(resp.model_name, resp.operation)
                return ChatResponse(
                    content=result,
                    kind="elevate",
                )
            else:
                return ChatResponse(
                    content=f"You requested an invalid model. Choose from\n{render_markdown(MODELS)}",
                    kind="elevate",
                    error=True,
                )

    if isinstance(resp, ModelTrainAPI):
        with lock:
            if not resp.model_name:
                return ChatResponse(
                    content=f"You requested an invalid model to train. Choose from\n{render_markdown(MODELS)}",
                    kind="error",
                    error=True,
                )

            svc = ModelFactory.create(resp.model_name)
            val = svc.val_train(request.prompt)

            if val.test_size is None or not (0 <= val.test_size <= 1):
                return ChatResponse(
                    content="test_size must be between 0 and 1",
                    kind="error",
                    error=True,
                )

            result = svc.train(val)

            content = f"`{result.get('model_name')}` trained with test_size=`{result.get('test_size')}` resulting in accuracy of `{result.get('accuracy')}`"
            mr.set_model_stage("titanic", "elevate")

            return ChatResponse(
                content=content,
                kind="train",
                metadata={
                    "train_results": result,
                },
            )

    if isinstance(resp, ModelInferenceAPI):
        with lock:
            if not active_model:
                return ChatResponse(
                    content="No model is currently in Production. Ask me to elevate a model first.",
                    kind="error",
                    error=True,
                )

            svc = ModelFactory.create(active_model)
            val = svc.val_inference(request.prompt)

            if val.missing_details:
                incomplete_response = svc.missing_response(val.missing_details)
                return ChatResponse(
                    content=incomplete_response,
                    kind="missing_inputs",
                    metadata={
                        "valid_values": svc.valid_values(),
                    },
                )

            features = svc.transform(val)
            raw_pred = svc.predict(
                features
            )  # TODO: change to preds with array of pred/proba?
            content = svc.format_response(raw_pred)

            return ChatResponse(
                content=content,
                kind="inference",
                metadata={
                    "raw_prediction": raw_pred,
                    "model_name": svc.model_name,
                },
            )

    # TODO: add a help intent router
    # if isinstance(resp, HelpUser):

    # TODO: inject list of approved actions
    # Guardrail
    if isinstance(resp, NonApprovedRequest):
        return ChatResponse(
            content="This is not an approved request. Try again.",
            kind="error",
            error=True,
        )
