from pydantic import BaseModel
from fastapi import FastAPI
import mlflow
from mlflow.tracking import MlflowClient
from dotenv import load_dotenv

from .baml_client import b
from .baml_client.types import ModelRegistryAPI, NonApprovedRequest


load_dotenv()

MLFLOW_TRACKING_URI="http://127.0.0.1:5000/"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Default")

client = MlflowClient()

app = FastAPI(title="ML_LLM Ops Demo - Backend APIs", version="0.0.1")

class ChatRequest(BaseModel):
    prompt: str

# TODO: find home later
def list_models():
    models = client.search_registered_models()
    return [model.name for model in models]

@app.get("/")
def home():
    return {"message": "Hello!"}

@app.post("/chat")
def chat(request: ChatRequest):
    resp = b.SelectTool(request.prompt)
    # TODO: will handle intent responses later...
    if isinstance(resp, ModelRegistryAPI):
        result = list_models()

    # TODO: inject list of approved actions
    elif isinstance(resp, NonApprovedRequest):
        result = "This is not an approved request. You may ask about <insert_list> later.."
    return {"models": result} 
