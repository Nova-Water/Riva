from fastapi.testclient import TestClient

from app.main import app


def test_message_without_llm_configured_returns_helpful_fallback():
    with TestClient(app) as client:
        resp = client.post("/assistant/message", json={"text": "What is the PC status?"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["kind"] == "message"
    assert "not configured" in body["content"].lower() or "limited mode" in body["content"].lower()
    assert body["conversation_id"]


def test_confirm_with_unknown_confirmation_id_returns_410():
    with TestClient(app) as client:
        resp = client.post(
            "/assistant/confirm",
            json={"conversation_id": "does-not-exist", "confirmation_id": "does-not-exist", "approve": True},
        )
    assert resp.status_code == 410
