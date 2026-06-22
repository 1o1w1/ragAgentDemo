from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from api.chat import chat_router, set_agent_behavior, get_agent_behavior
from main import create_app


@pytest.fixture
def mock_agent():
    agent = MagicMock()
    agent.chat.return_value = {
        "answer": "This is a test answer.",
        "citations": [
            {"index": 1, "source": "test.md", "content": "test content"}
        ],
        "has_context": True,
    }
    agent.get_conversation_history.return_value = [
        {"role": "user", "content": "test question", "metadata": {}, "timestamp": "2024-01-01T00:00:00"},
        {"role": "assistant", "content": "test answer", "metadata": {}, "timestamp": "2024-01-01T00:00:01"},
    ]
    return agent


@pytest.fixture
def app(mock_agent):
    set_agent_behavior(mock_agent)
    application = create_app()
    return application


@pytest.fixture
def client(app):
    return TestClient(app)


class TestChatEndpoint:
    def test_chat_success(self, client, mock_agent):
        response = client.post("/api/chat/", json={"query": "What is RAG?"})
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "This is a test answer."
        assert len(data["citations"]) == 1
        assert data["has_context"] is True
        mock_agent.chat.assert_called_once_with("What is RAG?")

    def test_chat_empty_query(self, client):
        response = client.post("/api/chat/", json={"query": ""})
        assert response.status_code == 422

    def test_chat_no_context(self, client, mock_agent):
        mock_agent.chat.return_value = {
            "answer": "知识库中未找到相关信息，无法回答该问题。",
            "citations": [],
            "has_context": False,
        }
        response = client.post("/api/chat/", json={"query": "unknown topic"})
        assert response.status_code == 200
        data = response.json()
        assert data["has_context"] is False
        assert data["citations"] == []

    def test_chat_server_error(self, client, mock_agent):
        mock_agent.chat.side_effect = Exception("LLM error")
        response = client.post("/api/chat/", json={"query": "test"})
        assert response.status_code == 500


class TestStreamEndpoint:
    def test_chat_stream_post_calls_agent(self, client, mock_agent):
        mock_agent.chat_stream.return_value = iter([
            {"type": "token", "content": "token1"},
            {"type": "token", "content": "token2"},
            {"type": "citations", "citations": [{"index": 1, "source": "test.md", "content": "test"}], "has_context": True},
        ])
        
        response = client.post("/api/chat/stream", json={"query": "What is RAG?"})
        assert response.status_code == 200
        mock_agent.chat_stream.assert_called_once_with("What is RAG?")


class TestHistoryEndpoint:
    def test_get_history(self, client, mock_agent):
        response = client.get("/api/chat/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) == 2
        mock_agent.get_conversation_history.assert_called_once()

    def test_clear_history(self, client, mock_agent):
        response = client.delete("/api/chat/history")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_agent.clear_conversation.assert_called_once()


class TestHealthEndpoint:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
