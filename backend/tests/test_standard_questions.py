import pytest
from pathlib import Path
from rag.document_loader import DocumentLoader
from rag.text_splitter import TextSplitter


DOCS_DIR = Path(__file__).parent.parent / "docs"

STANDARD_QUESTIONS = [
    "Python 有哪些常用的标准库？",
    "什么是 Scrum 框架中的三个角色？",
    "关系型数据库有哪些范式？",
]

OUT_OF_CONTEXT_QUESTIONS = [
    "如何制作法式蓝莓马卡龙？",
]


@pytest.fixture
def document_loader():
    return DocumentLoader()


@pytest.fixture
def text_splitter():
    return TextSplitter(chunk_size=500, chunk_overlap=50)


@pytest.fixture
def loaded_documents(document_loader):
    return document_loader.load_directory(str(DOCS_DIR))


@pytest.fixture
def split_documents(loaded_documents, text_splitter):
    return text_splitter.split_documents(loaded_documents)


class TestDocumentLoading:
    def test_docs_directory_exists(self):
        assert DOCS_DIR.exists(), f"docs directory not found at {DOCS_DIR}"

    def test_all_markdown_files_exist(self):
        expected_files = [
            "python_guide.md",
            "machine_learning.md",
            "web_development.md",
            "database_design.md",
            "project_management.md",
        ]
        for filename in expected_files:
            file_path = DOCS_DIR / filename
            assert file_path.exists(), f"Expected file not found: {file_path}"

    def test_load_all_documents(self, loaded_documents):
        expected_filenames = {
            "python_guide.md",
            "machine_learning.md",
            "web_development.md",
            "database_design.md",
            "project_management.md",
        }
        loaded_filenames = {doc.metadata["filename"] for doc in loaded_documents}
        assert expected_filenames.issubset(loaded_filenames), (
            f"Missing expected documents. Expected {expected_filenames}, got {loaded_filenames}"
        )

    def test_document_metadata(self, loaded_documents):
        for doc in loaded_documents:
            assert "source" in doc.metadata
            assert "filename" in doc.metadata
            assert doc.metadata["file_type"] == ".md"

    def test_document_content_not_empty(self, loaded_documents):
        for doc in loaded_documents:
            assert len(doc.page_content) > 0, f"Document {doc.metadata.get('filename')} is empty"


class TestTextSplitting:
    def test_split_documents(self, split_documents):
        assert len(split_documents) > 0, "No chunks created after splitting"

    def test_chunk_size_limit(self, split_documents, text_splitter):
        for chunk in split_documents:
            assert len(chunk.page_content) <= text_splitter.chunk_size + 100

    def test_chunks_have_metadata(self, split_documents):
        for chunk in split_documents:
            assert "source" in chunk.metadata
            assert "filename" in chunk.metadata


class TestStandardQuestions:
    @pytest.mark.parametrize("question", STANDARD_QUESTIONS)
    def test_standard_question_keywords(self, question, loaded_documents):
        all_content = " ".join([doc.page_content for doc in loaded_documents])

        if "Python" in question and "标准库" in question:
            assert "标准库" in all_content or "标准库" in all_content
        elif "Scrum" in question:
            assert "Scrum" in all_content
        elif "范式" in question:
            assert "范式" in all_content

    def test_python_libs_in_docs(self, loaded_documents):
        python_doc = None
        for doc in loaded_documents:
            if doc.metadata.get("filename") == "python_guide.md":
                python_doc = doc
                break
        assert python_doc is not None
        assert "os" in python_doc.page_content
        assert "json" in python_doc.page_content
        assert "sys" in python_doc.page_content

    def test_scrum_in_docs(self, loaded_documents):
        pm_doc = None
        for doc in loaded_documents:
            if doc.metadata.get("filename") == "project_management.md":
                pm_doc = doc
                break
        assert pm_doc is not None
        assert "Product Owner" in pm_doc.page_content
        assert "Scrum Master" in pm_doc.page_content

    def test_database_normalization_in_docs(self, loaded_documents):
        db_doc = None
        for doc in loaded_documents:
            if doc.metadata.get("filename") == "database_design.md":
                db_doc = doc
                break
        assert db_doc is not None
        assert "第一范式" in db_doc.page_content
        assert "第二范式" in db_doc.page_content
        assert "第三范式" in db_doc.page_content


class TestOutOfContextQuestions:
    @pytest.mark.parametrize("question", OUT_OF_CONTEXT_QUESTIONS)
    def test_out_of_context_not_in_docs(self, question, loaded_documents):
        all_content = " ".join([doc.page_content for doc in loaded_documents])
        keywords = ["马卡龙", "蓝莓", "法式", "制作"]
        found_keywords = [kw for kw in keywords if kw in all_content]
        assert len(found_keywords) == 0, f"Found unexpected keywords in docs: {found_keywords}"

    @pytest.mark.parametrize("question", OUT_OF_CONTEXT_QUESTIONS)
    def test_out_of_context_retrieval(self, question, loaded_documents, text_splitter):
        chunks = text_splitter.split_documents(loaded_documents)
        all_chunk_content = " ".join([chunk.page_content for chunk in chunks])
        keywords = ["马卡龙", "蓝莓", "法式", "制作"]
        found_keywords = [kw for kw in keywords if kw in all_chunk_content]
        assert len(found_keywords) == 0
