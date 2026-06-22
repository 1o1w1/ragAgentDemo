import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from langchain_core.documents import Document
from rag.vector_store import VectorStoreManager
from rag.embeddings import EmbeddingManager


@pytest.fixture
def mock_embedding_manager():
    manager = MagicMock(spec=EmbeddingManager)
    manager.embed_query.return_value = [0.1, 0.2, 0.3]
    manager.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    return manager


@pytest.fixture
def mock_chroma():
    with patch("backend.rag.vector_store.Chroma") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance, mock_cls


def test_add_documents(mock_embedding_manager, mock_chroma):
    mock_instance, mock_cls = mock_chroma
    mock_instance.add_texts.return_value = ["id1", "id2"]

    manager = VectorStoreManager(mock_embedding_manager, persist_directory="/tmp/test_db")
    docs = [
        Document(page_content="doc one", metadata={"source": "a.txt"}),
        Document(page_content="doc two", metadata={"source": "b.txt"}),
    ]
    ids = manager.add_documents(docs)

    assert ids == ["id1", "id2"]
    mock_instance.add_texts.assert_called_once_with(
        texts=["doc one", "doc two"],
        metadatas=[{"source": "a.txt"}, {"source": "b.txt"}],
    )


def test_add_documents_empty(mock_embedding_manager, mock_chroma):
    manager = VectorStoreManager(mock_embedding_manager)
    ids = manager.add_documents([])

    assert ids == []


def test_similarity_search(mock_embedding_manager, mock_chroma):
    mock_instance, mock_cls = mock_chroma
    expected = [Document(page_content="result", metadata={"source": "a.txt"})]
    mock_instance.similarity_search.return_value = expected

    manager = VectorStoreManager(mock_embedding_manager)
    results = manager.similarity_search("test query", k=3)

    assert results == expected
    mock_instance.similarity_search.assert_called_once_with(query="test query", k=3)


def test_similarity_search_empty_query(mock_embedding_manager, mock_chroma):
    mock_instance, mock_cls = mock_chroma
    manager = VectorStoreManager(mock_embedding_manager)
    results = manager.similarity_search("")

    assert results == []
    mock_instance.similarity_search.assert_not_called()


def test_similarity_search_with_score(mock_embedding_manager, mock_chroma):
    mock_instance, mock_cls = mock_chroma
    doc = Document(page_content="result", metadata={})
    expected = [(doc, 0.5)]
    mock_instance.similarity_search_with_score.return_value = expected

    manager = VectorStoreManager(mock_embedding_manager)
    results = manager.similarity_search_with_score("query", k=2)

    assert results == expected
    mock_instance.similarity_search_with_score.assert_called_once_with(query="query", k=2)


def test_similarity_search_with_score_empty_query(mock_embedding_manager, mock_chroma):
    mock_instance, mock_cls = mock_chroma
    manager = VectorStoreManager(mock_embedding_manager)
    results = manager.similarity_search_with_score("")

    assert results == []


def test_delete_collection(mock_embedding_manager, mock_chroma):
    mock_instance, mock_cls = mock_chroma

    manager = VectorStoreManager(mock_embedding_manager)
    manager.delete_collection()

    mock_instance.delete_collection.assert_called_once()
    assert manager._vector_store is None


def test_get_collection_stats(mock_embedding_manager, mock_chroma):
    mock_instance, mock_cls = mock_chroma
    mock_collection = MagicMock()
    mock_collection.count.return_value = 42
    mock_collection.name = "test_collection"
    mock_instance._collection = mock_collection

    manager = VectorStoreManager(mock_embedding_manager)
    stats = manager.get_collection_stats()

    assert stats == {"count": 42, "name": "test_collection"}


def test_lazy_vector_store_creation(mock_embedding_manager, mock_chroma):
    mock_instance, mock_cls = mock_chroma

    manager = VectorStoreManager(mock_embedding_manager, persist_directory="/tmp/test_db")
    assert manager._vector_store is None

    manager._get_vector_store()
    assert manager._vector_store is not None

    mock_cls.assert_called_once_with(
        persist_directory="/tmp/test_db",
        embedding_function=mock_embedding_manager,
    )
