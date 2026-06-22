from typing import List, Tuple
from langchain_core.documents import Document
from rag.vector_store import VectorStoreManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Retriever:
    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ):
        self.vector_store_manager = vector_store_manager
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    def retrieve(self, query: str) -> List[Tuple[Document, float]]:
        if not query.strip():
            logger.warning("Empty query provided for retrieval")
            return []

        results = self.vector_store_manager.similarity_search_with_score(
            query=query, k=self.top_k
        )

        for doc, score in results:
            logger.debug(f"Score: {score:.4f} | Source: {doc.metadata.get('source', 'unknown')} | Content: {doc.page_content[:80]}...")

        filtered = [
            (doc, score) for doc, score in results if score <= self.similarity_threshold
        ]

        logger.info(
            f"Retrieved {len(results)} results, {len(filtered)} passed threshold "
            f"({self.similarity_threshold})"
        )
        return filtered

    def retrieve_documents(self, query: str) -> List[Document]:
        return [doc for doc, _ in self.retrieve(query)]

    def update_config(self, top_k: int = None, similarity_threshold: float = None):
        if top_k is not None:
            self.top_k = top_k
        if similarity_threshold is not None:
            self.similarity_threshold = similarity_threshold
