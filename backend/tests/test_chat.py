"""Tests for chat REST endpoints (non-streaming). LLM is mocked."""

import pytest
from unittest.mock import patch, AsyncMock


MOCK_RESPONSE = "Based on your symptoms, you may have a common cold. Stay hydrated and rest."


def mock_chat(*args, **kwargs):
    """Return a fixed response without calling Ollama."""
    return MOCK_RESPONSE


# ── REST chat endpoint ────────────────────────────────────────────

def test_chat_unauthenticated_allowed(client):
    """Anonymous users can chat (conversation not saved to DB)."""
    with patch("app.api.routes.chat.chat", new=AsyncMock(return_value=MOCK_RESPONSE)):
        resp = client.post("/api/chat/", json={"message": "I have a headache"})
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data
    assert "conversation_id" in data
    assert data["model_used"] is not None


def test_chat_authenticated_saves_conversation(client, auth_headers):
    """Authenticated chat should create a DB conversation record."""
    with patch("app.api.routes.chat.chat", new=AsyncMock(return_value=MOCK_RESPONSE)), \
         patch("app.api.routes.chat.generate_title", new=AsyncMock(return_value="Headache Query")):
        resp = client.post("/api/chat/", json={"message": "I have a headache"},
                           headers=auth_headers)
    assert resp.status_code == 200

    # Verify conversation was saved
    conv_id = resp.json()["conversation_id"]
    conv_resp = client.get(f"/api/chat/conversations/{conv_id}", headers=auth_headers)
    assert conv_resp.status_code == 200
    assert conv_resp.json()["title"] == "Headache Query"


def test_chat_empty_message_rejected(client, auth_headers):
    resp = client.post("/api/chat/", json={"message": ""}, headers=auth_headers)
    assert resp.status_code == 422


def test_chat_safety_override_for_emergency(client, auth_headers):
    """Emergency messages should get an override response, not an LLM call."""
    resp = client.post("/api/chat/",
                       json={"message": "I have severe chest pain and can't breathe"},
                       headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "EMERGENCY" in data["response"] or "911" in data["response"]
    assert data["urgency_level"] == 5


# ── Conversation history ──────────────────────────────────────────

def test_list_conversations_empty(client, auth_headers):
    resp = client.get("/api/chat/conversations", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


def test_list_conversations_unauthenticated(client):
    resp = client.get("/api/chat/conversations")
    assert resp.status_code == 401


def test_get_conversation_not_found(client, auth_headers):
    resp = client.get("/api/chat/conversations/nonexistent-id", headers=auth_headers)
    assert resp.status_code == 404


def test_get_conversation_other_user_denied(client, auth_headers):
    """User A cannot access User B's conversation."""
    # Create conversation as user A
    with patch("app.api.routes.chat.chat", new=AsyncMock(return_value=MOCK_RESPONSE)), \
         patch("app.api.routes.chat.generate_title", new=AsyncMock(return_value="Test")):
        resp = client.post("/api/chat/", json={"message": "hello"}, headers=auth_headers)
    conv_id = resp.json()["conversation_id"]

    # Register user B and try to access user A's conversation
    client.post("/api/auth/register", json={
        "email": "b@example.com", "username": "userb", "password": "pass1234"
    })
    login_b = client.post("/api/auth/login", data={"username": "userb", "password": "pass1234"})
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    resp_b = client.get(f"/api/chat/conversations/{conv_id}", headers=headers_b)
    assert resp_b.status_code == 404
