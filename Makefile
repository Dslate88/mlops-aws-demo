backend:
	uvicorn src.backend.main:app --reload

frontend:
	cd src/frontend && uv run streamlit run app.py

make lint:
	ruff check .

make format:
	ruff format
