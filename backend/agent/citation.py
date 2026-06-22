from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from langchain_core.documents import Document
from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class Citation:
    index: int
    source: str
    content: str
    score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "index": self.index,
            "source": self.source,
            "content": self.content,
        }
        if self.score is not None:
            result["score"] = self.score
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class CitationManager:
    def __init__(self, show_score: bool = False):
        self.show_score = show_score
        self.citations: List[Citation] = []

    def create_citations(self, docs: List[Document], scores: Optional[List[float]] = None) -> List[Citation]:
        self.citations = []
        seen_contents = set()  # 用于去重
        
        for i, doc in enumerate(docs):
            # 去重：基于文档内容
            content_hash = hash(doc.page_content.strip())
            if content_hash in seen_contents:
                logger.debug(f"Skipping duplicate document at index {i}")
                continue
            seen_contents.add(content_hash)
            
            score = scores[i] if scores and i < len(scores) else None
            citation = Citation(
                index=len(self.citations) + 1,  # 使用去重后的索引
                source=doc.metadata.get("source", "未知来源"),
                content=doc.page_content,
                score=score,
                metadata={k: v for k, v in doc.metadata.items() if k != "source"},
            )
            self.citations.append(citation)
        logger.info(f"Created {len(self.citations)} citations (deduplicated from {len(docs)} documents)")
        return self.citations

    def format_citations_text(self) -> str:
        if not self.citations:
            return ""

        parts = ["参考来源:"]
        for cite in self.citations:
            line = f"[{cite.index}] {cite.source}"
            if self.show_score and cite.score is not None:
                line += f" (相似度: {cite.score:.2f})"
            parts.append(line)
        return "\n".join(parts)

    def format_citations_markdown(self) -> str:
        if not self.citations:
            return ""

        parts = ["## 参考来源\n"]
        for cite in self.citations:
            line = f"- **[{cite.index}]** `{cite.source}`"
            if self.show_score and cite.score is not None:
                line += f" (相似度: {cite.score:.2f})"
            parts.append(line)
        return "\n".join(parts)

    def get_citations_for_response(self) -> List[Dict[str, Any]]:
        return [cite.to_dict() for cite in self.citations]

    def get_citation_by_index(self, index: int) -> Optional[Citation]:
        for cite in self.citations:
            if cite.index == index:
                return cite
        return None

    def clear(self):
        self.citations.clear()

    def update_config(self, show_score: bool = None):
        if show_score is not None:
            self.show_score = show_score
