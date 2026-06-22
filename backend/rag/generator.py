from typing import List, AsyncIterator
import json
import httpx
from langchain_core.documents import Document
from utils.logger import setup_logger

logger = setup_logger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "你是一个知识库问答助手。根据上下文信息回答问题。"
    "如果没有相关信息，明确回复'知识库中未找到相关信息'。"
    "请按以下结构组织回答：\n"
    "1. 先简要总结核心答案（2-3句话）\n"
    "2. 再展开详细说明\n"
    "3. 最后列出参考来源"
)


class Generator:
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        enable_thinking: bool = False,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.enable_thinking = enable_thinking
        self.base_url = (base_url or "http://localhost:11434/v1").rstrip("/")
        self.api_key = api_key or "ollama"
        self.http_client = httpx.AsyncClient(
            transport=httpx.AsyncHTTPTransport(http1=True, http2=False, verify=False),
            timeout=httpx.Timeout(60.0, connect=10.0),
        )

    def _ollama_url(self) -> str:
        return self.base_url.replace("/v1", "")

    def _build_ollama_messages(self, query: str, context_docs: List[Document]) -> list:
        context = self._build_context(context_docs)
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self._build_prompt(query, context)},
        ]

    async def generate(self, query: str, context_docs: List[Document]) -> dict:
        if not query.strip():
            logger.warning("Empty query provided for generation")
            return {"content": "", "reasoning": ""}

        messages = self._build_ollama_messages(query, context_docs)

        try:
            resp = await self.http_client.post(
                f"{self._ollama_url()}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "think": self.enable_thinking,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()
            msg = data.get("message", {})
            content = msg.get("content", "")
            reasoning = msg.get("thinking", "")
            return {"content": content, "reasoning": reasoning}
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def generate_stream(self, query: str, context_docs: List[Document]) -> AsyncIterator[dict]:
        if not query.strip():
            logger.warning("Empty query provided for generation")
            return

        messages = self._build_ollama_messages(query, context_docs)

        try:
            async with self.http_client.stream(
                "POST",
                f"{self._ollama_url()}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "think": self.enable_thinking,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                },
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    msg = chunk.get("message", {})
                    if msg.get("thinking"):
                        yield {"type": "reasoning", "text": msg["thinking"]}
                    if msg.get("content"):
                        yield {"type": "content", "text": msg["content"]}
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise

    def _build_context(self, docs: List[Document]) -> str:
        if not docs:
            return ""

        parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "未知来源")
            parts.append(f"[{i}] (来源: {source})\n{doc.page_content}")
        return "\n\n".join(parts)

    def _build_prompt(self, query: str, context: str) -> str:
        if not context:
            return f"问题: {query}\n\n注意: 知识库中未找到相关信息。"

        return (
            f"请根据以下上下文信息回答问题。\n\n"
            f"上下文:\n{context}\n\n"
            f"问题: {query}\n\n"
            f"请先给出总结性回答，再展开说明，最后引用来源。"
        )

    def update_config(
        self,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        system_prompt: str = None,
        api_key: str = None,
        base_url: str = None,
        enable_thinking: bool = None,
    ):
        if system_prompt is not None:
            self.system_prompt = system_prompt
        if model is not None:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if enable_thinking is not None:
            self.enable_thinking = enable_thinking
        if base_url is not None:
            self.base_url = base_url.rstrip("/")
        if api_key is not None:
            self.api_key = api_key
