from typing import List
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TextSplitter:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        if not documents:
            return []

        chunks = []
        for doc in documents:
            if not doc.page_content.strip():
                continue

            doc_chunks = self.splitter.split_documents([doc])
            for i, chunk in enumerate(doc_chunks):
                chunk.metadata['chunk_index'] = i
                chunk.metadata['total_chunks'] = len(doc_chunks)
                chunks.append(chunk)

        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks

    def split_text(self, text: str, metadata: dict = None) -> List[Document]:
        if not text.strip():
            return []

        if metadata is None:
            metadata = {}

        doc = Document(page_content=text, metadata=metadata)
        return self.split_documents([doc])

    def update_config(self, chunk_size: int = None, chunk_overlap: int = None):
        if chunk_size is not None:
            self.chunk_size = chunk_size
        if chunk_overlap is not None:
            self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
