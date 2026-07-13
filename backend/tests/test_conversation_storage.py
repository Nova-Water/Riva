from app.database import crud


def test_create_and_retrieve_conversation():
    convo = crud.create_conversation(title="Test Conversation")
    fetched = crud.get_conversation(convo.id)
    assert fetched is not None
    assert fetched.title == "Test Conversation"


def test_add_and_list_messages():
    convo = crud.create_conversation()
    crud.add_message(convo.id, "user", "Hello RIVA", "message")
    crud.add_message(convo.id, "assistant", "Hello! How can I help?", "message")

    messages = crud.get_recent_messages(convo.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"


def test_delete_conversation_removes_it():
    convo = crud.create_conversation()
    assert crud.delete_conversation(convo.id) is True
    assert crud.get_conversation(convo.id) is None


def test_clear_all_conversations():
    crud.create_conversation()
    crud.create_conversation()
    crud.clear_all_conversations()
    assert crud.list_conversations() == []


def test_record_and_list_email_draft():
    draft = crud.save_email_draft("client@example.com", "Quotation", "Please find attached.", "Project Alpha")
    drafts = crud.list_email_drafts()
    assert any(d.id == draft.id for d in drafts)
