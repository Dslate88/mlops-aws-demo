from fastapi import FastAPI


app = FastAPI(title="ML_LLM Ops Demo - Backend APIs", version="0.0.1")


@app.get("/")
def home():
    return {"message": "Hello!"}
