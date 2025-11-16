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
