from typing import List
import openai
import httpx
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EmbeddingManager:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "text-embedding-ada-002"):
        self.model = model
        transport = httpx.HTTPTransport(http1=True, http2=False)
        http_client = httpx.Client(transport=transport, timeout=httpx.Timeout(60.0))
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client,
        )

    def embed_query(self, text: str) -> List[float]:
        if not text.strip():
            logger.warning("Empty text provided for embedding")
            return []

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        valid_texts = [t for t in texts if t.strip()]
        if not valid_texts:
            logger.warning("All provided texts are empty")
            return []

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=valid_texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating document embeddings: {e}")
            return []

    def update_config(self, api_key: str = None, base_url: str = None, model: str = None):
        if model is not None:
            self.model = model
        if api_key is not None or base_url is not None:
            self.client = openai.OpenAI(
                api_key=api_key or self.client.api_key,
                base_url=base_url or self.client.base_url,
            )
