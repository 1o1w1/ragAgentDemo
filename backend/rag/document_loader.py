from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DocumentLoader:
    def __init__(self):
        self.supported_extensions = {'.md', '.txt'}

    def load_file(self, file_path: str) -> List[Document]:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return []

        if path.suffix not in self.supported_extensions:
            logger.warning(f"Unsupported file type: {path.suffix}")
            return []

        try:
            loader = TextLoader(str(path), encoding='utf-8')
            documents = loader.load()

            for doc in documents:
                doc.metadata['source'] = str(path)
                doc.metadata['filename'] = path.name
                doc.metadata['file_type'] = path.suffix

            logger.info(f"Loaded {len(documents)} documents from {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return []

    def load_directory(self, directory_path: str, patterns: List[str] = None) -> List[Document]:
        path = Path(directory_path)
        if not path.exists():
            logger.error(f"Directory not found: {directory_path}")
            return []

        if patterns is None:
            patterns = ["**/*.md", "**/*.txt"]

        all_documents = []
        for pattern in patterns:
            for file_path in path.glob(pattern):
                if file_path.is_file():
                    documents = self.load_file(str(file_path))
                    all_documents.extend(documents)

        logger.info(f"Loaded {len(all_documents)} documents from directory {directory_path}")
        return all_documents

    def load_uploaded_file(self, file_path: str, original_filename: str) -> List[Document]:
        documents = self.load_file(file_path)
        for doc in documents:
            doc.metadata['original_filename'] = original_filename

        return documents
