REGION ?= us-east-1
ACCOUNT_ID ?= $(shell aws sts get-caller-identity --query Account --output text)

BACKEND_REPO = mlops-demo-backend
FRONTEND_REPO = mlops-demo-frontend

TAG ?= $(shell git rev-parse --short HEAD)
LATEST_TAG = latest

IMAGE_PREFIX = $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com
BACKEND_IMAGE  = $(BACKEND_REPO):$(TAG)
FRONTEND_IMAGE = $(FRONTEND_REPO):$(TAG)
BACKEND_ECR_IMAGE  = $(IMAGE_PREFIX)/$(BACKEND_REPO):$(TAG)
FRONTEND_ECR_IMAGE = $(IMAGE_PREFIX)/$(FRONTEND_REPO):$(TAG)
BACKEND_ECR_IMAGE_LATEST  = $(IMAGE_PREFIX)/$(BACKEND_REPO):$(LATEST_TAG)
FRONTEND_ECR_IMAGE_LATEST = $(IMAGE_PREFIX)/$(FRONTEND_REPO):$(LATEST_TAG)

backend:
	uvicorn src.backend.main:app --reload

frontend:
	cd src/frontend && uv run streamlit run app.py

lint:
	ruff check .

format:
	ruff format

test:
	pytest

mlflow:
	mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

baml-dev:
	uv run baml-cli dev --from src/backend

docker-up:
	docker compose up --build

ecr-auth:
	aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

docker-build-backend:
	docker build --platform=linux/amd64 -f Dockerfile.backend -t $(BACKEND_IMAGE) .

docker-build-frontend:
	docker build --platform=linux/amd64 -f Dockerfile.frontend -t $(FRONTEND_IMAGE) .

docker-build-all: docker-build-backend docker-build-frontend

docker-tag-backend: docker-build-backend
	docker tag $(BACKEND_IMAGE) $(BACKEND_ECR_IMAGE)
	docker tag $(BACKEND_IMAGE) $(BACKEND_ECR_IMAGE_LATEST)

docker-tag-frontend: docker-build-frontend
	docker tag $(FRONTEND_IMAGE) $(FRONTEND_ECR_IMAGE)
	docker tag $(FRONTEND_IMAGE) $(FRONTEND_ECR_IMAGE_LATEST)

docker-tag-all: docker-tag-backend docker-tag-frontend

docker-push-backend: ecr-auth docker-tag-backend
	docker push $(BACKEND_ECR_IMAGE)
	docker push $(BACKEND_ECR_IMAGE_LATEST)

docker-push-frontend: ecr-auth docker-tag-frontend
	docker push $(FRONTEND_ECR_IMAGE)
	docker push $(FRONTEND_ECR_IMAGE_LATEST)

docker-push-all: docker-push-backend docker-push-frontend
