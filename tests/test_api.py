from fastapi.testclient import TestClient

from assistant_app.api.app import app


client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_endpoint() -> None:
    response = client.post("/chat", json={"message": "O que é CDB?", "session_id": "api-test"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == "api-test"
    assert "Aviso:" in payload["answer"]
