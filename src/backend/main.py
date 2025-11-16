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
def list_models():
    models = client.search_registered_models()
    return [model.name for model in models]

def get_latest_version(model_name):
    versions = client.search_model_versions(f"name='{model_name}'")
    return max([x.version for x in versions])

def stage_model(stage: ModelStageAPI):
    tgt = "Production" if stage.operation == "elevate" else stage.operation
    v_id = get_latest_version(stage.model_name)
    client.set_model_version_tag(
        name=stage.model_name,
        version=v_id,
        key="app_stage",
        value=tgt
    )

# ########################################################
@app.get("/")
def home():
    return {"message": "Hello!"}

@app.post("/chat")
def chat(request: ChatRequest):
    resp = b.SelectTool(request.prompt)
    # TODO: will handle intent responses later...
    if isinstance(resp, ModelRegistryAPI):
        result = list_models()
        return {"models": result} 

    if isinstance(resp, ModelStageAPI):
        # TODO: error handle if model_name does not exist, then inform user of valid models they can select
        result = stage_model(resp)
        return {"resp": resp} 

    # TODO: inject list of approved actions
    elif isinstance(resp, NonApprovedRequest):
        result = "This is not an approved request. You may ask about <insert_list> later.."
        return {"Denied": result} 
