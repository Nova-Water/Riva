from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok():
    with TestClient(app) as client:
        resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "RIVA AI"


def test_config_status_reports_unconfigured_llm_without_key():
    with TestClient(app) as client:
        resp = client.get("/config/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["llm"]["configured"] is False


def test_tools_endpoint_lists_registered_tools():
    with TestClient(app) as client:
        resp = client.get("/tools")
    assert resp.status_code == 200
    names = {t["name"] for t in resp.json()}
    assert "get_pc_status" in names


def test_no_api_key_leaks_in_config_status_response():
    with TestClient(app) as client:
        resp = client.get("/config/status")
    assert "ADD_YOUR_LLM_API_KEY" not in resp.text
