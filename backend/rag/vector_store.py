from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from rag.embeddings import EmbeddingManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class VectorStoreManager:
    def __init__(self, embedding_manager: EmbeddingManager, persist_directory: str = "./chroma_db"):
        self.embedding_manager = embedding_manager
        self.persist_directory = persist_directory
        self._vector_store = None

    def _get_vector_store(self) -> Chroma:
        if self._vector_store is None:
            self._vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_manager,
            )
        return self._vector_store

    def add_documents(self, documents: List[Document], batch_size: int = 10) -> List[str]:
        if not documents:
            logger.warning("No documents provided to add")
            return []

        try:
            vector_store = self._get_vector_store()
            all_ids = []
            total = len(documents)

            for i in range(0, total, batch_size):
                batch = documents[i:i + batch_size]
                texts = [doc.page_content for doc in batch]
                metadatas = [doc.metadata for doc in batch]
                ids = vector_store.add_texts(texts=texts, metadatas=metadatas)
                all_ids.extend(ids)
                logger.info(f"Embedded {min(i + batch_size, total)}/{total} chunks")

            logger.info(f"Added {len(all_ids)} documents to vector store")
            return all_ids
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return []

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if not query.strip():
            logger.warning("Empty query provided for similarity search")
            return []

        try:
            vector_store = self._get_vector_store()
            results = vector_store.similarity_search(query=query, k=k)
            logger.info(f"Found {len(results)} similar documents for query")
            return results
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            return []

    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        if not query.strip():
            logger.warning("Empty query provided for similarity search")
            return []

        try:
            vector_store = self._get_vector_store()
            results = vector_store.similarity_search_with_score(query=query, k=k)
            logger.info(f"Found {len(results)} similar documents with scores")
            return results
        except Exception as e:
            logger.error(f"Error performing similarity search with scores: {e}")
            return []

    def delete_collection(self):
        try:
            vector_store = self._get_vector_store()
            vector_store.delete_collection()
            self._vector_store = None
            logger.info("Deleted vector store collection")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")

    def get_collection_stats(self) -> dict:
        try:
            vector_store = self._get_vector_store()
            collection = vector_store._collection
            return {
                "count": collection.count(),
                "name": collection.name,
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"count": 0, "name": "unknown"}
