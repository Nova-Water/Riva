"""Manual verification script (not part of the pytest suite): drives the full
agent loop — including a real tool_call, a real confirmation_required amber
tool, and the confirm/approve flow — using a stub LLM provider, since this
sandboxed environment has no real LLM API key available.

Run with: python tests/manual_smoke_stub_llm.py
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

os.environ["RIVA_DATA_DIRECTORY"] = tempfile.mkdtemp(prefix="riva-smoke-")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.providers.llm.base import LLMMessage, LLMProvider, LLMResponse  # noqa: E402
from app.state import get_state  # noqa: E402


class StubLLMProvider(LLMProvider):
    name = "stub"

    def __init__(self):
        self.calls = 0

    def is_configured(self) -> bool:
        return True

    async def complete(self, messages: list[LLMMessage], *, timeout_seconds: float = 30.0) -> LLMResponse:
        self.calls += 1
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")

        if "pc status" in last_user.lower() and self.calls == 1:
            return LLMResponse(raw_text='{"type": "tool_call", "tool_name": "get_pc_status", "arguments": {}}', model="stub")
        if "pc status" in last_user.lower() and self.calls == 2:
            return LLMResponse(raw_text='{"type": "message", "content": "Your PC looks healthy."}', model="stub")
        if "create" in last_user.lower() and "document" in last_user.lower():
            return LLMResponse(
                raw_text=(
                    '{"type": "confirmation_required", "tool_name": "create_document", '
                    '"arguments": {"filename": "smoke-test.md", "content": "# Smoke test"}, '
                    '"confirmation_message": "Create smoke-test.md?"}'
                ),
                model="stub",
            )
        return LLMResponse(raw_text='{"type": "message", "content": "OK."}', model="stub")


def main() -> None:
    with TestClient(app) as client:
        state = get_state()
        stub = StubLLMProvider()
        state.llm_provider = stub
        state.agent._llm = stub  # noqa: SLF001

        print("1) Sending 'What is the PC status?' (expects green tool_call -> auto-run -> message)")
        resp = client.post("/assistant/message", json={"text": "What is the PC status?"})
        body = resp.json()
        assert resp.status_code == 200, body
        assert body["kind"] == "message", body
        assert body["tool_activity"], "expected tool_activity to be populated"
        assert body["tool_activity"][0]["tool_name"] == "get_pc_status"
        assert body["tool_activity"][0]["success"] is True
        print("   OK:", body["content"])
        conversation_id = body["conversation_id"]

        print("2) Sending 'Please create a document' (expects amber confirmation_required)")
        resp = client.post("/assistant/message", json={"conversation_id": conversation_id, "text": "Please create a document"})
        body = resp.json()
        assert resp.status_code == 200, body
        assert body["kind"] == "confirmation_required", body
        confirmation_id = body["confirmation_id"]
        print("   OK: confirmation requested ->", body["confirmation_message"])

        print("3) Approving the confirmation (expects the file to actually be created)")
        resp = client.post(
            "/assistant/confirm",
            json={"conversation_id": conversation_id, "confirmation_id": confirmation_id, "approve": True},
        )
        body = resp.json()
        assert resp.status_code == 200, body
        assert body["tool_activity"][0]["success"] is True, body
        created_path = Path(os.environ["RIVA_DATA_DIRECTORY"]) / "documents" / "smoke-test.md"
        assert created_path.exists(), f"expected {created_path} to exist"
        assert created_path.read_text() == "# Smoke test"
        print("   OK: file created at", created_path)

        print("4) Verifying conversation persistence across a fresh GET /conversations/{id}")
        resp = client.get(f"/conversations/{conversation_id}")
        body = resp.json()
        assert resp.status_code == 200
        assert len(body["messages"]) >= 4
        print("   OK:", len(body["messages"]), "messages persisted")

        print("5) Rejecting a second confirmation (expects tool NOT to run)")
        resp = client.post("/assistant/message", json={"conversation_id": conversation_id, "text": "Please create a document"})
        confirmation_id_2 = resp.json()["confirmation_id"]
        resp = client.post(
            "/assistant/confirm",
            json={"conversation_id": conversation_id, "confirmation_id": confirmation_id_2, "approve": False},
        )
        assert resp.status_code == 200
        assert "won't go ahead" in resp.json()["content"].lower()
        print("   OK: rejection handled without running the tool")

    print("\nALL SMOKE CHECKS PASSED")


if __name__ == "__main__":
    main()
