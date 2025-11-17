from pydantic import BaseModel
from fastapi import FastAPI
import mlflow
from mlflow.tracking import MlflowClient
from dotenv import load_dotenv

from .baml_client import b
from .baml_client.types import ModelRegistryAPI, ModelStageAPI, NonApprovedRequest 


load_dotenv()

MLFLOW_TRACKING_URI="http://127.0.0.1:5000/"
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
            name=model_name,
            version=version,
            key="app_stage",
            value=target_stage
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
            return {"content": f"You requested an invalid model. Choose from\n{render_markdown(MODELS)}"} 


    # TODO: inject list of approved actions
    elif isinstance(resp, NonApprovedRequest):
        result = "This is not an approved request. You may ask about <insert_list> later.."
        return {"content": result} 
