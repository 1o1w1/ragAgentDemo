import pytest
from unittest.mock import MagicMock, patch
from rag.embeddings import EmbeddingManager


@pytest.fixture
def mock_openai_client():
    with patch("backend.rag.embeddings.openai.OpenAI") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        yield mock_client


def test_embed_query_returns_embedding(mock_openai_client):
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
    mock_openai_client.embeddings.create.return_value = mock_response

    manager = EmbeddingManager(api_key="test-key", model="text-embedding-ada-002")
    result = manager.embed_query("test query")

    assert result == [0.1, 0.2, 0.3]
    mock_openai_client.embeddings.create.assert_called_once_with(
        model="text-embedding-ada-002",
        input="test query",
    )


def test_embed_query_empty_text(mock_openai_client):
    manager = EmbeddingManager(api_key="test-key")
    result = manager.embed_query("")

    assert result == []
    mock_openai_client.embeddings.create.assert_not_called()


def test_embed_documents_returns_embeddings(mock_openai_client):
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=[0.1, 0.2]),
        MagicMock(embedding=[0.3, 0.4]),
    ]
    mock_openai_client.embeddings.create.return_value = mock_response

    manager = EmbeddingManager(api_key="test-key")
    result = manager.embed_documents(["doc one", "doc two"])

    assert result == [[0.1, 0.2], [0.3, 0.4]]
    mock_openai_client.embeddings.create.assert_called_once_with(
        model="text-embedding-ada-002",
        input=["doc one", "doc two"],
    )


def test_embed_documents_empty_list(mock_openai_client):
    manager = EmbeddingManager(api_key="test-key")
    result = manager.embed_documents([])

    assert result == []
    mock_openai_client.embeddings.create.assert_not_called()


def test_embed_documents_filters_empty_texts(mock_openai_client):
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.5, 0.6])]
    mock_openai_client.embeddings.create.return_value = mock_response

    manager = EmbeddingManager(api_key="test-key")
    result = manager.embed_documents(["", "  ", "valid text"])

    assert result == [[0.5, 0.6]]
    mock_openai_client.embeddings.create.assert_called_once_with(
        model="text-embedding-ada-002",
        input=["valid text"],
    )


def test_embed_query_api_error(mock_openai_client):
    mock_openai_client.embeddings.create.side_effect = Exception("API Error")

    manager = EmbeddingManager(api_key="test-key")
    result = manager.embed_query("test")

    assert result == []


def test_embed_documents_api_error(mock_openai_client):
    mock_openai_client.embeddings.create.side_effect = Exception("API Error")

    manager = EmbeddingManager(api_key="test-key")
    result = manager.embed_documents(["test"])

    assert result == []


def test_update_config_model(mock_openai_client):
    manager = EmbeddingManager(api_key="test-key", model="old-model")
    manager.update_config(model="new-model")

    assert manager.model == "new-model"


def test_custom_base_url():
    with patch("backend.rag.embeddings.openai.OpenAI") as mock_cls, \
         patch("backend.rag.embeddings.httpx.Client") as mock_httpx_client:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_http_client = MagicMock()
        mock_httpx_client.return_value = mock_http_client

        manager = EmbeddingManager(
            api_key="test-key",
            base_url="https://custom.api.com/v1",
            model="custom-model",
        )

        mock_cls.assert_called_once_with(
            api_key="test-key",
            base_url="https://custom.api.com/v1",
            http_client=mock_http_client,
        )
        assert manager.model == "custom-model"
