import pytest
from rag.text_splitter import TextSplitter
from langchain_core.documents import Document


def test_split_short_document():
    splitter = TextSplitter(chunk_size=100, chunk_overlap=20)
    doc = Document(page_content="Short document content.")

    chunks = splitter.split_documents([doc])

    assert len(chunks) == 1
    assert chunks[0].page_content == "Short document content."


def test_split_long_document():
    splitter = TextSplitter(chunk_size=50, chunk_overlap=10)
    content = "This is a test document. " * 10  # 250 characters
    doc = Document(page_content=content, metadata={'source': 'test.md'})

    chunks = splitter.split_documents([doc])

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.page_content) <= 50
        assert chunk.metadata['source'] == 'test.md'


def test_split_preserves_metadata():
    splitter = TextSplitter(chunk_size=50, chunk_overlap=10)
    doc = Document(
        page_content="Test content for splitting.",
        metadata={'source': 'test.md', 'filename': 'test.md'}
    )

    chunks = splitter.split_documents([doc])

    for chunk in chunks:
        assert chunk.metadata['source'] == 'test.md'
        assert chunk.metadata['filename'] == 'test.md'


def test_split_empty_document():
    splitter = TextSplitter()
    doc = Document(page_content="")

    chunks = splitter.split_documents([doc])

    assert len(chunks) == 0
