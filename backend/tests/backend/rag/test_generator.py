import pytest
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from rag.generator import Generator, DEFAULT_SYSTEM_PROMPT


@pytest.fixture
def mock_openai():
    with patch("backend.rag.generator.openai") as mock:
        mock_client = MagicMock()
        mock.OpenAI.return_value = mock_client
        yield mock_client


def test_generate_with_context(mock_openai):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "这是回答"
    mock_openai.chat.completions.create.return_value = mock_response

    docs = [
        Document(page_content="文档内容", metadata={"source": "test.md"}),
    ]

    generator = Generator(api_key="test-key")
    result = generator.generate("问题", docs)

    assert result == "这是回答"
    mock_openai.chat.completions.create.assert_called_once()

    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    messages = call_kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == DEFAULT_SYSTEM_PROMPT
    assert "文档内容" in messages[1]["content"]
    assert "问题" in messages[1]["content"]


def test_generate_without_context(mock_openai):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "知识库中未找到相关信息"
    mock_openai.chat.completions.create.return_value = mock_response

    generator = Generator(api_key="test-key")
    result = generator.generate("问题", [])

    assert result == "知识库中未找到相关信息"
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    messages = call_kwargs["messages"]
    assert "未找到相关信息" in messages[1]["content"]


def test_generate_empty_query(mock_openai):
    generator = Generator(api_key="test-key")
    result = generator.generate("", [])

    assert result == ""
    mock_openai.chat.completions.create.assert_not_called()


def test_generate_whitespace_query(mock_openai):
    generator = Generator(api_key="test-key")
    result = generator.generate("   ", [])

    assert result == ""
    mock_openai.chat.completions.create.assert_not_called()


def test_build_context_with_source(mock_openai):
    docs = [
        Document(page_content="内容一", metadata={"source": "a.md"}),
        Document(page_content="内容二", metadata={"source": "b.md"}),
    ]

    generator = Generator(api_key="test-key")
    context = generator._build_context(docs)

    assert "[1] (来源: a.md)" in context
    assert "内容一" in context
    assert "[2] (来源: b.md)" in context
    assert "内容二" in context


def test_build_context_without_source(mock_openai):
    docs = [Document(page_content="内容", metadata={})]

    generator = Generator(api_key="test-key")
    context = generator._build_context(docs)

    assert "未知来源" in context


def test_build_context_empty(mock_openai):
    generator = Generator(api_key="test-key")
    context = generator._build_context([])

    assert context == ""


def test_build_prompt_with_context(mock_openai):
    generator = Generator(api_key="test-key")
    prompt = generator._build_prompt("问题", "上下文内容")

    assert "上下文内容" in prompt
    assert "问题" in prompt


def test_build_prompt_without_context(mock_openai):
    generator = Generator(api_key="test-key")
    prompt = generator._build_prompt("问题", "")

    assert "未找到相关信息" in prompt


def test_custom_system_prompt(mock_openai):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "回答"
    mock_openai.chat.completions.create.return_value = mock_response

    custom_prompt = "自定义提示词"
    generator = Generator(api_key="test-key", system_prompt=custom_prompt)
    generator.generate("问题", [])

    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    messages = call_kwargs["messages"]
    assert messages[0]["content"] == custom_prompt


def test_llm_init_params(mock_openai):
    with patch("backend.rag.generator.httpx.Client") as mock_httpx_client:
        mock_http_client = MagicMock()
        mock_httpx_client.return_value = mock_http_client

        Generator(
            api_key="sk-test",
            base_url="https://custom.api.com/v1",
            model="gpt-4",
            temperature=0.5,
            max_tokens=1000,
        )

        from rag.generator import openai

        openai.OpenAI.assert_called_with(
            api_key="sk-test",
            base_url="https://custom.api.com/v1",
            http_client=mock_http_client,
        )


def test_generate_llm_error_propagates(mock_openai):
    mock_openai.chat.completions.create.side_effect = RuntimeError("API error")

    generator = Generator(api_key="test-key")

    with pytest.raises(RuntimeError, match="API error"):
        generator.generate("问题", [Document(page_content="c", metadata={})])


def test_citations_in_prompt(mock_openai):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "回答"
    mock_openai.chat.completions.create.return_value = mock_response

    docs = [
        Document(page_content="第一段", metadata={"source": "doc1.md"}),
        Document(page_content="第二段", metadata={"source": "doc2.md"}),
    ]

    generator = Generator(api_key="test-key")
    generator.generate("问题", docs)

    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    prompt = call_kwargs["messages"][1]["content"]
    assert "[1]" in prompt
    assert "doc1.md" in prompt
    assert "[2]" in prompt
    assert "doc2.md" in prompt


def test_update_config(mock_openai):
    generator = Generator(api_key="test-key", system_prompt="old")
    generator.update_config(system_prompt="new", model="gpt-4", temperature=0.3)

    assert generator.system_prompt == "new"
    assert generator.model == "gpt-4"
    assert generator.temperature == 0.3


def test_generate_passes_model_params(mock_openai):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "回答"
    mock_openai.chat.completions.create.return_value = mock_response

    generator = Generator(
        api_key="test-key", model="gpt-4", temperature=0.3, max_tokens=500
    )
    generator.generate("问题", [Document(page_content="c", metadata={})])

    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "gpt-4"
    assert call_kwargs["temperature"] == 0.3
    assert call_kwargs["max_tokens"] == 500


def test_generate_stream_with_context(mock_openai):
    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [MagicMock()]
    mock_chunk1.choices[0].delta.content = "这是"
    
    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [MagicMock()]
    mock_chunk2.choices[0].delta.content = "回答"
    
    mock_chunk3 = MagicMock()
    mock_chunk3.choices = [MagicMock()]
    mock_chunk3.choices[0].delta.content = None
    
    mock_openai.chat.completions.create.return_value = [mock_chunk1, mock_chunk2, mock_chunk3]

    docs = [
        Document(page_content="文档内容", metadata={"source": "test.md"}),
    ]

    generator = Generator(api_key="test-key")
    tokens = list(generator.generate_stream("问题", docs))

    assert tokens == ["这是", "回答"]
    mock_openai.chat.completions.create.assert_called_once()
    
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["stream"] is True
    messages = call_kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == DEFAULT_SYSTEM_PROMPT
    assert "文档内容" in messages[1]["content"]
    assert "问题" in messages[1]["content"]


def test_generate_stream_without_context(mock_openai):
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "知识库中未找到相关信息"
    
    mock_openai.chat.completions.create.return_value = [mock_chunk]

    generator = Generator(api_key="test-key")
    tokens = list(generator.generate_stream("问题", []))

    assert tokens == ["知识库中未找到相关信息"]
    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    messages = call_kwargs["messages"]
    assert "未找到相关信息" in messages[1]["content"]


def test_generate_stream_empty_query(mock_openai):
    generator = Generator(api_key="test-key")
    tokens = list(generator.generate_stream("", []))

    assert tokens == []
    mock_openai.chat.completions.create.assert_not_called()


def test_generate_stream_whitespace_query(mock_openai):
    generator = Generator(api_key="test-key")
    tokens = list(generator.generate_stream("   ", []))

    assert tokens == []
    mock_openai.chat.completions.create.assert_not_called()


def test_generate_stream_passes_model_params(mock_openai):
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "回答"
    
    mock_openai.chat.completions.create.return_value = [mock_chunk]

    generator = Generator(
        api_key="test-key", model="gpt-4", temperature=0.3, max_tokens=500
    )
    list(generator.generate_stream("问题", [Document(page_content="c", metadata={})]))

    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "gpt-4"
    assert call_kwargs["temperature"] == 0.3
    assert call_kwargs["max_tokens"] == 500
    assert call_kwargs["stream"] is True


def test_generate_stream_error_propagates(mock_openai):
    mock_openai.chat.completions.create.side_effect = RuntimeError("API error")

    generator = Generator(api_key="test-key")

    with pytest.raises(RuntimeError, match="API error"):
        list(generator.generate_stream("问题", [Document(page_content="c", metadata={})]))


def test_generate_stream_custom_system_prompt(mock_openai):
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "回答"
    
    mock_openai.chat.completions.create.return_value = [mock_chunk]

    custom_prompt = "自定义提示词"
    generator = Generator(api_key="test-key", system_prompt=custom_prompt)
    list(generator.generate_stream("问题", []))

    call_kwargs = mock_openai.chat.completions.create.call_args[1]
    messages = call_kwargs["messages"]
    assert messages[0]["content"] == custom_prompt
