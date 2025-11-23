# mlops-aws-demo

Still actively developing, plan to continue working on this the next few weeks.

My goal here is twofold:
1) demonstrate a variety of skillsets, not create a 100% practical application
2) have a repo I can continue to experiment with new patterns/architectures, etc (see section 7 below for example)

My perspective on LLM's:
- allow it to help reason, but rarely code for you.
    - for example, I had AI generate an outline for this README.md that I then wrote myself, it refactored my streamlit logic, and reasoned over multiple design patterns along the way. 
- find ways to bulid LLM's into process for automations/productivity, example [aws-strands-sops](https://aws.amazon.com/blogs/opensource/introducing-strands-agent-sops-natural-language-workflows-for-ai-agents/)

What this demo delivers:
- LLM intent routing: 
- FastAPI backend
- MLflow model registry + [ONNX](https://onnx.ai/) (wanted to experiment with it)
- Streamlit chat UI 
- AWS ECS/Fargate deployment (secure enough to be considered overkill for this demo, my preference..)

Things I plan to add (list will grow)
- explore auto-updating docs via llm pattern [aws-blog-topic](https://aws.amazon.com/blogs/opensource/introducing-strands-agent-sops-natural-language-workflows-for-ai-agents/)
- replace [baml](https://github.com/BoundaryML/baml) with [pydantic-ai](https://ai.pydantic.dev/)
- make user interaction pattern more natural with pydantic-ai patterns
- build structlog pattern
- build/automate ml monitoring patterns
- potentially carve out training into microservice and actually train/tune large models


> see [Issue #3: mlops-aws-demo development summary](https://github.com/Dslate88/mlops-aws-demo/issues/3).

## 1. What this demo does

So, basically its a user input (langauage) based way of triggering common MLOps patterns. 

At a high level:
1. Users interact with a securly hosted Streamlit frontend.
2. User input is processed by FastAPI backend /chat route
3. /chat route handles the intent routing allowing the actions below:
   - list models in the MLFlow Registry
   - elevate/archive a model (rule that only 1 active model at a time)
   - remove a model
   - train a model
   - run inference with the active production model
  

Would recommend poking around in the codebase, but a few areas to poke around might be:
- [ModelRegistry](https://github.com/Dslate88/mlops-aws-demo/blob/main/src/backend/models/registry.py) as a proxy for commonly seen business logic requirements
- and [ModelFactory](https://github.com/Dslate88/mlops-aws-demo/blob/main/src/backend/models/factory.py) + [BaseModelService](https://github.com/Dslate88/mlops-aws-demo/blob/main/src/backend/models/factory.py) + [TitanicModelService](https://github.com/Dslate88/mlops-aws-demo/blob/main/src/backend/models/titanic.py) as a pattern for scaling ML/LLM systems. For instance, the [transform method](https://github.com/Dslate88/mlops-aws-demo/blob/ace562b735b6c568a192de04720ef6b99456bf55/src/backend/models/titanic.py#L59-L71) has a easy path to integrating with features stores. 

## 2. AWS deployment
My terraform in the [infra](https://github.com/Dslate88/mlops-aws-demo/tree/main/infra) folder defines everything this needs to run and be accessible by anyone. 
I tend to prefer building repeatable stacks that can be consumed and rapidly deployed, for instance rapidly deploying a ML model (or anything) via importing a terraform module...but im not demonstrating that currently in this project. 

If I were thinking production:
- I wouldn't be using my simple threading.Lock pattern
- terraform would be stored in dynamodb/s3 at a mininum
- terraform would be in a module pattern
- pattern to train/log/register models built independently and with env/dependency flexibility, aka remove train method from my service pattern.
    - alternatives vary, but sagemaker endpoints, databricks, etc.
- secrets would be in Github and/or AWS Secrets Manager, with iam policies to consume secrets on containers during start up.
- I wouldnt be hosting my own MLflow on a container, preference a hosted service like Sagemaker or Databricks.
- would need enterprise level logging of applicaiton activity
- would configure CICD GHA patterns that auto-deploy feature branches to the cloud for testing (related to prior terraform module details)
- leverage terraform module work to create CICD patterns for dev/qa/prod deployments, potentially based on release hooks if needed
- Despite public/private subnet architecture enforcing 443 port, thats not enough for enterprise as you want to lock down ingress from company CIDR blocks
    - Related, a user authentication mechanism to ensure you are a valid enterprise member (i.e. Azure AD) in the public layer prior to private layer redirect.
- More security, image scanning for vulnerabilites, etc.
- tests
  
## dev notes (aka document later)
- pipx usage
- pipx install uv
- pipx install ruff
- source .venv/bin/activate
- short-term key bedrock
- makefile
- compose + containers

---

### Everything below was ai-generated. I have a keymap that I push that consumes all my active files and injects a goal, for instance: "generate an outline of topics to cover in my README.md"

## 3. Core components 

### 3.1 LLM intent router (BAML) 
The router is defined in `src/backend/baml_src/main.baml`:

`SelectTool(user_message: string)` decides which intent class to return:

- `ModelRegistryAPI` – list/query models in MLflow.
- `ModelStageAPI` – elevate or archive a model.
- `ModelInferenceAPI` – run inference on the current production model.
- `ModelTrainAPI` – trigger a training run for a model.
- `ModelRemoveAPI` – delete a model from the registry.
- `NonApprovedRequest` – everything else.

Additional BAML definitions in `titanic.baml` handle:
- Parsing user messages into structured TitanicInput (inference features).
- Parsing training configs into TitanicTrain (e.g., test_size).

### 3.2 Backend (FastAPI) 

`src/backend/main.py` exposes:

- `GET /health` – basic health check.
- `GET /active-model` – returns the current production model and its version (via ModelRegistry).
- `POST /chat` – main entry point for the LLM router and model operations.

Key backend pieces: 

#### ModelRegistry (`src/backend/models/registry.py`):

- Wraps `mlflow.tracking.MlflowClient`.
- Tracks the latest version of each registered model.
- Reads/writes an `app_stage` tag to represent Production / Archived.
- Enforces that only one model can be in Production at a time by archiving any existing production models when a new one is elevated.

#### ModelFactory (`src/backend/models/factory.py`):

Maps a `model_name` string to a concrete service class.

Currently:

```python
registry = {
    "titanic": TitanicModelService,
    # "insurance": InsuranceModelService,  # future extension
}
```

This is the extension point for hosting multiple models under a common API.

#### Pydantic models:

- `ChatRequest` – user prompt string.
- `ChatResponse` – content, kind (intent type), error flag, and optional metadata.
- `ActiveModelResponse` – name + version of the production model.

### 3.3 Model services, ONNX, and MLflow

`BaseModelService` (`src/backend/models/base.py`) defines an abstract interface for model services:

- `transform(...)` – convert validated input into feature dict.
- `valid_values()` – report valid categorical values for UX/help.
- `build_feed(features)` – build ONNX input tensors.
- `predict(features)` – shared ONNX inference logic via mlflow/onnx.
- `format_response(raw_pred)` – user-facing phrasing of predictions.
- `train(config)` – train a model and log it to MLflow.

#### TitanicModelService (`src/backend/models/titanic.py`):

- Loads the classic Titanic dataset via `seaborn.load_dataset("titanic")`.
- Uses a Pipeline with ColumnTransformer + OneHotEncoder + LogisticRegression.
- Converts the trained pipeline to ONNX with `skl2onnx.to_onnx`.
- Logs the ONNX model into MLflow:

```python
mlflow.onnx.log_model(..., registered_model_name=self.model_name)
```

At inference time:

- `BaseModelService.get_session()` calls `mlflow.onnx.load_model("models:/{model_name}/latest")`.
- Runs inference with `onnxruntime.InferenceSession`.

### 3.4 Frontend (Streamlit)

`src/frontend/app.py` implements a simple chat-style UI:

#### Main pane

- Banner showing the active production model (via `/active-model`).
- Chat history rendered with `st.chat_message`.
- A single user input where:
  - The user types a prompt, or
  - A sidebar button injects a suggested message into the next request.

The UI interprets `ChatResponse.kind` to render helpful tips or metadata:

- Show valid values when inputs are missing.
- Show training metrics when a training run completes.
- Show raw prediction metadata for inference responses.
