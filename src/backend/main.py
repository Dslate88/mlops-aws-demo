from fastapi import FastAPI
import mlflow
from mlflow.tracking import MlflowClient

MLFLOW_TRACKING_URI="http://127.0.0.1:5000/"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Default")

client = MlflowClient()

models = client.search_registered_models()

app = FastAPI(title="ML_LLM Ops Demo - Backend APIs", version="0.0.1")

@app.get("/")
def home():
    return {"message": "Hello!"}

@app.get("/list_models")
def list_models():
    models = client.search_registered_models()
    names = [model.name for model in models]
    return {"names": names}
