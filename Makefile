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
