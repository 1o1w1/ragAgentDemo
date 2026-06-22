import pytest
from langchain_core.documents import Document
from agent.citation import CitationManager, Citation


def test_create_citations():
    manager = CitationManager()
    docs = [
        Document(page_content="内容一", metadata={"source": "doc1.md"}),
        Document(page_content="内容二", metadata={"source": "doc2.md"}),
    ]

    citations = manager.create_citations(docs)

    assert len(citations) == 2
    assert citations[0].index == 1
    assert citations[0].source == "doc1.md"
    assert citations[0].content == "内容一"
    assert citations[1].index == 2
    assert citations[1].source == "doc2.md"


def test_create_citations_with_scores():
    manager = CitationManager(show_score=True)
    docs = [
        Document(page_content="内容一", metadata={"source": "doc1.md"}),
        Document(page_content="内容二", metadata={"source": "doc2.md"}),
    ]
    scores = [0.95, 0.87]

    citations = manager.create_citations(docs, scores)

    assert citations[0].score == 0.95
    assert citations[1].score == 0.87


def test_create_citations_without_source():
    manager = CitationManager()
    docs = [Document(page_content="内容", metadata={})]

    citations = manager.create_citations(docs)

    assert citations[0].source == "未知来源"


def test_format_citations_text():
    manager = CitationManager()
    docs = [
        Document(page_content="内容一", metadata={"source": "doc1.md"}),
        Document(page_content="内容二", metadata={"source": "doc2.md"}),
    ]
    manager.create_citations(docs)

    text = manager.format_citations_text()

    assert "参考来源:" in text
    assert "[1] doc1.md" in text
    assert "[2] doc2.md" in text


def test_format_citations_text_with_score():
    manager = CitationManager(show_score=True)
    docs = [Document(page_content="内容", metadata={"source": "doc.md"})]
    manager.create_citations(docs, scores=[0.95])

    text = manager.format_citations_text()

    assert "相似度: 0.95" in text


def test_format_citations_markdown():
    manager = CitationManager()
    docs = [
        Document(page_content="内容一", metadata={"source": "doc1.md"}),
        Document(page_content="内容二", metadata={"source": "doc2.md"}),
    ]
    manager.create_citations(docs)

    md = manager.format_citations_markdown()

    assert "## 参考来源" in md
    assert "**[1]**" in md
    assert "`doc1.md`" in md


def test_format_citations_empty():
    manager = CitationManager()
    assert manager.format_citations_text() == ""
    assert manager.format_citations_markdown() == ""


def test_get_citations_for_response():
    manager = CitationManager()
    docs = [Document(page_content="内容", metadata={"source": "doc.md", "page": 1})]
    manager.create_citations(docs)

    response = manager.get_citations_for_response()

    assert len(response) == 1
    assert response[0]["index"] == 1
    assert response[0]["source"] == "doc.md"
    assert response[0]["metadata"] == {"page": 1}


def test_get_citation_by_index():
    manager = CitationManager()
    docs = [
        Document(page_content="内容一", metadata={"source": "doc1.md"}),
        Document(page_content="内容二", metadata={"source": "doc2.md"}),
    ]
    manager.create_citations(docs)

    cite = manager.get_citation_by_index(2)
    assert cite is not None
    assert cite.source == "doc2.md"

    assert manager.get_citation_by_index(99) is None


def test_clear():
    manager = CitationManager()
    docs = [Document(page_content="内容", metadata={"source": "doc.md"})]
    manager.create_citations(docs)

    manager.clear()

    assert len(manager.citations) == 0
    assert manager.format_citations_text() == ""


def test_update_config():
    manager = CitationManager(show_score=False)
    manager.update_config(show_score=True)

    assert manager.show_score is True


def test_citation_to_dict():
    citation = Citation(index=1, source="test.md", content="内容", score=0.9, metadata={"page": 1})
    d = citation.to_dict()

    assert d["index"] == 1
    assert d["source"] == "test.md"
    assert d["content"] == "内容"
    assert d["score"] == 0.9
    assert d["metadata"] == {"page": 1}


def test_citation_to_dict_no_score():
    citation = Citation(index=1, source="test.md", content="内容")
    d = citation.to_dict()

    assert "score" not in d
