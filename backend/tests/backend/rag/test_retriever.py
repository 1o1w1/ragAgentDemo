import pytest
from unittest.mock import MagicMock
from langchain_core.documents import Document
from rag.retriever import Retriever
from rag.vector_store import VectorStoreManager


@pytest.fixture
def mock_vector_store_manager():
    manager = MagicMock(spec=VectorStoreManager)
    return manager


def test_retrieve_with_threshold_filtering(mock_vector_store_manager):
    doc1 = Document(page_content="relevant", metadata={"source": "a.txt"})
    doc2 = Document(page_content="less relevant", metadata={"source": "b.txt"})
    doc3 = Document(page_content="irrelevant", metadata={"source": "c.txt"})
    mock_vector_store_manager.similarity_search_with_score.return_value = [
        (doc1, 0.3),
        (doc2, 0.6),
        (doc3, 0.8),
    ]

    retriever = Retriever(
        mock_vector_store_manager, top_k=5, similarity_threshold=0.7
    )
    results = retriever.retrieve("test query")

    assert len(results) == 2
    assert results[0] == (doc1, 0.3)
    assert results[1] == (doc2, 0.6)


def test_retrieve_all_filtered_out(mock_vector_store_manager):
    doc = Document(page_content="far", metadata={})
    mock_vector_store_manager.similarity_search_with_score.return_value = [
        (doc, 0.9),
    ]

    retriever = Retriever(
        mock_vector_store_manager, top_k=5, similarity_threshold=0.5
    )
    results = retriever.retrieve("query")

    assert results == []


def test_retrieve_empty_query(mock_vector_store_manager):
    retriever = Retriever(mock_vector_store_manager)
    results = retriever.retrieve("")

    assert results == []
    mock_vector_store_manager.similarity_search_with_score.assert_not_called()


def test_retrieve_whitespace_query(mock_vector_store_manager):
    retriever = Retriever(mock_vector_store_manager)
    results = retriever.retrieve("   ")

    assert results == []
    mock_vector_store_manager.similarity_search_with_score.assert_not_called()


def test_retrieve_passes_top_k(mock_vector_store_manager):
    mock_vector_store_manager.similarity_search_with_score.return_value = []

    retriever = Retriever(mock_vector_store_manager, top_k=3)
    retriever.retrieve("query")

    mock_vector_store_manager.similarity_search_with_score.assert_called_once_with(
        query="query", k=3
    )


def test_retrieve_documents_returns_only_docs(mock_vector_store_manager):
    doc1 = Document(page_content="a", metadata={})
    doc2 = Document(page_content="b", metadata={})
    mock_vector_store_manager.similarity_search_with_score.return_value = [
        (doc1, 0.2),
        (doc2, 0.4),
    ]

    retriever = Retriever(mock_vector_store_manager, similarity_threshold=0.5)
    docs = retriever.retrieve_documents("query")

    assert docs == [doc1, doc2]


def test_update_config(mock_vector_store_manager):
    retriever = Retriever(
        mock_vector_store_manager, top_k=5, similarity_threshold=0.7
    )
    retriever.update_config(top_k=10, similarity_threshold=0.9)

    assert retriever.top_k == 10
    assert retriever.similarity_threshold == 0.9


def test_update_config_partial(mock_vector_store_manager):
    retriever = Retriever(
        mock_vector_store_manager, top_k=5, similarity_threshold=0.7
    )
    retriever.update_config(top_k=10)

    assert retriever.top_k == 10
    assert retriever.similarity_threshold == 0.7


def test_threshold_boundary(mock_vector_store_manager):
    doc = Document(page_content="boundary", metadata={})
    mock_vector_store_manager.similarity_search_with_score.return_value = [
        (doc, 0.7),
    ]

    retriever = Retriever(
        mock_vector_store_manager, similarity_threshold=0.7
    )
    results = retriever.retrieve("query")

    assert len(results) == 1


def test_retrieve_exception_propagates(mock_vector_store_manager):
    mock_vector_store_manager.similarity_search_with_score.side_effect = RuntimeError(
        "db error"
    )

    retriever = Retriever(mock_vector_store_manager)

    with pytest.raises(RuntimeError, match="db error"):
        retriever.retrieve("query")
