from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_home_status_code_is_200():
    response = client.get("/")
    assert response.status_code == 200


def test_home_response_body():
    response = client.get("/")
    assert response.json() == {"message": "Hello!"}
