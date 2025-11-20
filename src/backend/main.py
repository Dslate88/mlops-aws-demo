import os
from pydantic import BaseModel
from fastapi import FastAPI
import mlflow
from mlflow.tracking import MlflowClient
from dotenv import load_dotenv
import onnxruntime as rt
import numpy as np
from typing import Optional, Literal

from .baml_client import b
from .baml_client.types import (
    ModelRegistryAPI,
    ModelStageAPI,
    NonApprovedRequest,
    ModelInferenceAPI,
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


class ChatRequest(BaseModel):
    prompt: str

# TODO: keep elevate as only action, remove ability to archive in baml layer...
class ChatResponse(BaseModel):
    content: str
    kind: Literal[
        "list_models",
        "elevate",
        "missing_inputs",
        "inference",
        "error"
    ]
    error: bool = False
    metadata: Optional[dict] = None


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


@app.post("/chat")
def chat(request: ChatRequest):
    MODELS = mr.list_models()
    active_model = mr.get_production_model()
    resp = b.SelectTool(request.prompt)

    # List Registry Models
    if isinstance(resp, ModelRegistryAPI):
        return ChatResponse(
            content=render_markdown(MODELS),
            kind="list_models",
        )

    # Elevate/Archive Models
    if isinstance(resp, ModelStageAPI):
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
                error=True
            )

    # Predict f(x)
    if isinstance(resp, ModelInferenceAPI):
        # Confirm a model is in Production
        if not active_model:
            return ChatResponse(
                content="No model is currently in Production. Ask me to elevate a model first.",
                kind="error",
                error=True
            )

        # Factory Pattern
        svc, validate_fn = ModelFactory.create(active_model)

        # Extract features from user input
        val = validate_fn(request.prompt)

        # Handle incomplete features (if any)
        if val.missing_details:
            incomplete_response = svc.missing_response(val.missing_details)
            return ChatResponse(
                content=incomplete_response,
                kind="missing_inputs",
                metadata= {
                    "valid_values": svc.valid_values(),
                },
            )

        # Run Inference
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

    # TODO: inject list of approved actions
    # Guardrail
    if isinstance(resp, NonApprovedRequest):
        return ChatResponse(
            content="This is not an approved request. Try again.",
            kind="error",
            error=True
        )
