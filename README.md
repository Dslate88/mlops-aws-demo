## initial idea:
- ui interface that allows:
    - text input to describe ml environment (error_rate, inferences_per_minute, etc)
    - text input to elevate/switch models (traditional supervised ml models)
        - NOTE: would need modern frontend stack to handle callbacks for friendly "processing" messages...try to just use something like streamlit for simplicity
    - interface acts as input payload through micro agent(baml?) pattern, sending to endpoint for inference?
    - based on active model, input callback to user, submit validation prior to inference

## target arch?:
- backend-app: fastapi
- frontend: streamlit, react, django...?
- aws_infra: ec2 vs ecs vs sagemaker
- networking: igw > public > secure to private
- stateful: dynamodb
- data versioning: dvc? mlflow hybrid?
- model registry: just use mlflow...? tf spin up service?
- llm provider: try out aws ecosystem...llama

## iteration approach/thoughts/braindump:
- setup core backend/frontend on respective infra W/O caring about securing traffic until later
- stage1: local working
- stage2: minimal aws working
- stage3: aws improvements (networking, bundling, etc)

## dev notes (aka document later)
- pipx usage
- pipx install uv
- pipx install ruff
