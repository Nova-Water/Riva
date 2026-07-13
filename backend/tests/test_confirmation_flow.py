import time

from app.security.confirmation import ConfirmationStore


def test_confirmation_is_created_and_popped():
    store = ConfirmationStore()
    pending = store.create("convo-1", "create_document", {"filename": "a.md"}, "Create a.md?")
    popped = store.pop(pending.confirmation_id)
    assert popped is not None
    assert popped.tool_name == "create_document"
    # Popping again returns nothing — a confirmation can only be used once.
    assert store.pop(pending.confirmation_id) is None


def test_confirmation_expires_after_ttl(monkeypatch):
    store = ConfirmationStore()
    pending = store.create("convo-1", "create_document", {}, "Create?")
    pending.created_at = time.time() - 10_000  # force expiry
    assert store.pop(pending.confirmation_id) is None


def test_unknown_confirmation_id_returns_none():
    store = ConfirmationStore()
    assert store.pop("does-not-exist") is None
