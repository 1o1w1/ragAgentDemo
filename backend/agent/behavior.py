from typing import List, Dict, Any, Optional, AsyncIterator
from langchain_core.documents import Document
from agent.conversation import ConversationManager
from agent.citation import CitationManager, Citation
from rag.retriever import Retriever
from rag.generator import Generator
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AgentBehavior:
    def __init__(
        self,
        retriever: Retriever,
        generator: Generator,
        max_history: int = 10,
        refuse_when_no_context: bool = True,
        show_citation_score: bool = False,
    ):
        self.retriever = retriever
        self.generator = generator
        self.refuse_when_no_context = refuse_when_no_context
        self.conversation = ConversationManager(max_history=max_history)
        self.citation_manager = CitationManager(show_score=show_citation_score)

    async def chat(self, query: str) -> Dict[str, Any]:
        if not query.strip():
            logger.warning("Empty query provided")
            return {"answer": "", "citations": [], "has_context": False}

        self.conversation.add_user_message(query)

        docs_with_scores = self.retriever.retrieve(query)
        docs = [doc for doc, _ in docs_with_scores]
        scores = [score for _, score in docs_with_scores]

        has_context = len(docs) > 0

        if not has_context and self.refuse_when_no_context:
            answer = "知识库中未找到相关信息，无法回答该问题。"
            self.conversation.add_assistant_message(answer)
            logger.info("No context found, refusing to answer")
            return {"answer": answer, "citations": [], "has_context": False}

        citations = self.citation_manager.create_citations(docs, scores)

        deduped_docs = self._deduplicate_docs(docs)
        result = await self.generator.generate(query, deduped_docs)
        answer = result["content"]
        reasoning = result.get("reasoning", "")

        self.conversation.add_assistant_message(
            answer, metadata={"has_context": has_context, "citation_count": len(citations)}
        )

        logger.info(f"Generated answer with {len(citations)} citations")
        return {
            "answer": answer,
            "reasoning": reasoning,
            "citations": self.citation_manager.get_citations_for_response(),
            "has_context": has_context,
        }

    async def chat_stream(self, query: str) -> AsyncIterator[dict]:
        """流式聊天，返回token和citations事件"""
        if not query.strip():
            logger.warning("Empty query provided")
            return

        self.conversation.add_user_message(query)

        docs_with_scores = self.retriever.retrieve(query)
        docs = [doc for doc, _ in docs_with_scores]
        scores = [score for _, score in docs_with_scores]

        has_context = len(docs) > 0

        if not has_context and self.refuse_when_no_context:
            answer = "知识库中未找到相关信息，无法回答该问题。"
            self.conversation.add_assistant_message(answer)
            logger.info("No context found, refusing to answer")
            yield {"type": "token", "content": answer}
            return

        citations = self.citation_manager.create_citations(docs, scores)

        deduped_docs = self._deduplicate_docs(docs)
        full_answer = ""
        full_reasoning = ""
        async for chunk in self.generator.generate_stream(query, deduped_docs):
            if chunk["type"] == "content":
                full_answer += chunk["text"]
                yield {"type": "token", "content": chunk["text"]}
            elif chunk["type"] == "reasoning":
                full_reasoning += chunk["text"]
                yield {"type": "reasoning", "content": chunk["text"]}

        self.conversation.add_assistant_message(
            full_answer, metadata={"has_context": has_context, "citation_count": len(citations)}
        )

        yield {
            "type": "citations",
            "citations": self.citation_manager.get_citations_for_response(),
            "has_context": has_context,
        }

        logger.info(f"Generated streaming answer with {len(citations)} citations")

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        return self.conversation.get_history()

    def get_formatted_citations(self, format_type: str = "text") -> str:
        if format_type == "markdown":
            return self.citation_manager.format_citations_markdown()
        return self.citation_manager.format_citations_text()

    def clear_conversation(self):
        self.conversation.clear()
        self.citation_manager.clear()
        logger.info("Conversation and citations cleared")

    def _deduplicate_docs(self, docs: List[Document]) -> List[Document]:
        seen = set()
        deduped = []
        for doc in docs:
            content_hash = hash(doc.page_content.strip())
            if content_hash not in seen:
                seen.add(content_hash)
                deduped.append(doc)
        if len(deduped) < len(docs):
            logger.info(f"Deduplicated docs: {len(docs)} -> {len(deduped)}")
        return deduped

    def update_config(
        self,
        max_history: int = None,
        refuse_when_no_context: bool = None,
        show_citation_score: bool = None,
    ):
        if max_history is not None:
            self.conversation.update_config(max_history=max_history)
        if refuse_when_no_context is not None:
            self.refuse_when_no_context = refuse_when_no_context
        if show_citation_score is not None:
            self.citation_manager.update_config(show_score=show_citation_score)
