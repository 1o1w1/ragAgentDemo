import pytest
import tempfile
from pathlib import Path
from rag.document_loader import DocumentLoader


def test_load_markdown_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Test\n\nThis is a test document.")
        file_path = f.name

    loader = DocumentLoader()
    documents = loader.load_file(file_path)

    assert len(documents) == 1
    assert documents[0].page_content == "# Test\n\nThis is a test document."
    assert documents[0].metadata['source'] == file_path

    Path(file_path).unlink()


def test_load_text_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Plain text content.")
        file_path = f.name

    loader = DocumentLoader()
    documents = loader.load_file(file_path)

    assert len(documents) == 1
    assert documents[0].page_content == "Plain text content."

    Path(file_path).unlink()


def test_load_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        md_file = Path(temp_dir) / "test.md"
        md_file.write_text("# Markdown\n\nContent here.")

        txt_file = Path(temp_dir) / "test.txt"
        txt_file.write_text("Text content.")

        loader = DocumentLoader()
        documents = loader.load_directory(temp_dir)

        assert len(documents) == 2
        sources = [doc.metadata['source'] for doc in documents]
        assert str(md_file) in sources
        assert str(txt_file) in sources


def test_unsupported_file_type():
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        file_path = f.name

    loader = DocumentLoader()
    documents = loader.load_file(file_path)

    assert len(documents) == 0

    Path(file_path).unlink()
