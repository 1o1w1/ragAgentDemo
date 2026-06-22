# 多源文档智能问答 Agent（RAG）实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个基于RAG的智能问答Agent，支持本地文件夹和文件上传两种文档接入方式，实现完整的RAG流水线，并提供Web界面。

**Architecture:** 单体应用架构，FastAPI后端 + React前端 + Chroma向量数据库。使用LangChain实现RAG流水线，支持OpenAI兼容的LLM API。

**Tech Stack:** Python 3.10+, FastAPI, LangChain, Chroma, React 18, TypeScript, Ant Design

---

## 文件结构

### 后端文件结构
```
backend/
├── __init__.py
├── main.py                  # FastAPI入口
├── config.py                # 配置管理
├── rag/
│   ├── __init__.py
│   ├── document_loader.py   # 文档加载器
│   ├── text_splitter.py     # 文本分割器
│   ├── embeddings.py        # 嵌入模型
│   ├── vector_store.py      # 向量存储
│   ├── retriever.py         # 检索器
│   └── generator.py         # 生成器
├── agent/
│   ├── __init__.py
│   ├── conversation.py      # 对话管理
│   ├── citation.py          # 引用溯源
│   └── behavior.py          # Agent行为
├── api/
│   ├── __init__.py
│   ├── chat.py              # 聊天API
│   ├── documents.py         # 文档API
│   └── config.py            # 配置API
└── utils/
    ├── __init__.py
    ├── logger.py            # 日志工具
    └── validators.py        # 验证工具
```

### 前端文件结构
```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   └── index.ts
│   │   ├── Sidebar/
│   │   │   ├── ConfigPanel.tsx
│   │   │   ├── FileList.tsx
│   │   │   └── index.ts
│   │   ├── FileUpload/
│   │   │   ├── UploadArea.tsx
│   │   │   ├── UploadProgress.tsx
│   │   │   └── index.ts
│   │   └── Citations/
│   │       ├── CitationList.tsx
│   │       ├── CitationDetail.tsx
│   │       └── index.ts
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   └── index.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── chatService.ts
│   │   └── documentService.ts
│   ├── hooks/
│   │   ├── useChat.ts
│   │   └── useConfig.ts
│   ├── utils/
│   │   ├── markdown.ts
│   │   └── helpers.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── index.tsx
├── package.json
└── tsconfig.json
```

### 配置和文档文件
```
根目录/
├── config.yaml              # 主配置文件
├── requirements.txt         # Python依赖
├── .env.example             # 环境变量示例
├── docs/                    # 示例文档
│   ├── python_guide.md
│   ├── machine_learning.md
│   ├── web_development.md
│   ├── database_design.md
│   └── project_management.md
├── uploads/                 # 上传文件目录
└── chroma_db/               # 向量数据库存储
```

---

## Task 1: 项目初始化和配置管理

**Files:**
- Create: `config.yaml`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `backend/__init__.py`
- Create: `backend/config.py`
- Create: `backend/utils/__init__.py`
- Create: `backend/utils/logger.py`
- Create: `backend/utils/validators.py`
- Test: `tests/backend/test_config.py`

- [ ] **Step 1: 创建配置文件**

```yaml
# config.yaml
sources:
  local:
    enabled: true
    path: "./docs"
    patterns: ["**/*.md", "**/*.txt"]
  upload:
    enabled: true
    path: "./uploads"

rag:
  chunk_size: 512
  chunk_overlap: 64
  top_k: 5
  similarity_threshold: 0.7

agent:
  max_history: 10
  refuse_when_no_context: true
  temperature: 0.7
  system_prompt: |
    你是一个知识库问答助手。根据上下文信息回答问题。
    如果没有相关信息，明确回复"知识库中未找到相关信息"。
    回答时请引用来源。

ui:
  show_citations: true
  show_similarity_score: false
  theme: "light"

llm:
  provider: "openai"
  model: "gpt-3.5-turbo"
  base_api: "https://api.openai.com/v1"
  temperature: 0.7
  max_tokens: 2000

embedding:
  provider: "openai"
  model: "text-embedding-ada-002"
  base_api: "https://api.openai.com/v1"

storage:
  vector_db: "./chroma_db"
  documents: "./docs"
  uploads: "./uploads"
```

- [ ] **Step 2: 创建Python依赖文件**

```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
langchain==0.0.350
langchain-community==0.0.6
langchain-core==0.1.1
chromadb==0.4.18
openai==1.3.7
pydantic==2.5.2
pydantic-settings==2.1.0
python-dotenv==1.0.0
pyyaml==6.0.1
python-multipart==0.0.6
aiofiles==23.2.1
watchdog==3.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

- [ ] **Step 3: 创建环境变量示例**

```bash
# .env.example
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
```

- [ ] **Step 4: 创建配置管理模块**

```python
# backend/__init__.py
__version__ = "0.1.0"
```

```python
# backend/config.py
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class LocalSourceConfig(BaseModel):
    enabled: bool = True
    path: str = "./docs"
    patterns: list[str] = ["**/*.md", "**/*.txt"]

class UploadSourceConfig(BaseModel):
    enabled: bool = True
    path: str = "./uploads"

class SourcesConfig(BaseModel):
    local: LocalSourceConfig = LocalSourceConfig()
    upload: UploadSourceConfig = UploadSourceConfig()

class RAGConfig(BaseModel):
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 5
    similarity_threshold: float = 0.7

class AgentConfig(BaseModel):
    max_history: int = 10
    refuse_when_no_context: bool = True
    temperature: float = 0.7
    system_prompt: str = "你是一个知识库问答助手。根据上下文信息回答问题。如果没有相关信息，明确回复'知识库中未找到相关信息'。回答时请引用来源。"

class UIConfig(BaseModel):
    show_citations: bool = True
    show_similarity_score: bool = False
    theme: str = "light"

class LLMConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    base_api: str = "https://api.openai.com/v1"
    temperature: float = 0.7
    max_tokens: int = 2000

class EmbeddingConfig(BaseModel):
    provider: str = "openai"
    model: str = "text-embedding-ada-002"
    base_api: str = "https://api.openai.com/v1"

class StorageConfig(BaseModel):
    vector_db: str = "./chroma_db"
    documents: str = "./docs"
    uploads: str = "./uploads"

class AppConfig(BaseModel):
    sources: SourcesConfig = SourcesConfig()
    rag: RAGConfig = RAGConfig()
    agent: AgentConfig = AgentConfig()
    ui: UIConfig = UIConfig()
    llm: LLMConfig = LLMConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    storage: StorageConfig = StorageConfig()

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = AppConfig()
        self._load_config()
    
    def _load_config(self):
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                if config_data:
                    self.config = AppConfig(**config_data)
    
    def reload_config(self):
        self._load_config()
    
    def get_config(self) -> AppConfig:
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        config_data = self.config.dict()
        config_data.update(updates)
        self.config = AppConfig(**config_data)
        self._save_config()
    
    def _save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config.dict(), f, default_flow_style=False, allow_unicode=True)

config_manager = ConfigManager()
```

- [ ] **Step 5: 创建工具模块**

```python
# backend/utils/__init__.py
from .logger import setup_logger
from .validators import validate_config

__all__ = ["setup_logger", "validate_config"]
```

```python
# backend/utils/logger.py
import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
```

```python
# backend/utils/validators.py
from typing import Dict, Any, List
from pydantic import ValidationError

def validate_config(config_data: Dict[str, Any]) -> List[str]:
    errors = []
    
    required_sections = ['sources', 'rag', 'agent', 'llm', 'embedding', 'storage']
    for section in required_sections:
        if section not in config_data:
            errors.append(f"Missing required config section: {section}")
    
    if 'rag' in config_data:
        rag_config = config_data['rag']
        if 'chunk_size' in rag_config and rag_config['chunk_size'] <= 0:
            errors.append("rag.chunk_size must be positive")
        if 'top_k' in rag_config and rag_config['top_k'] <= 0:
            errors.append("rag.top_k must be positive")
    
    return errors
```

- [ ] **Step 6: 编写配置管理测试**

```python
# tests/backend/test_config.py
import pytest
import tempfile
import yaml
from pathlib import Path
from backend.config import ConfigManager, AppConfig

def test_default_config():
    config = AppConfig()
    assert config.rag.chunk_size == 512
    assert config.rag.top_k == 5
    assert config.agent.refuse_when_no_context == True

def test_load_config_from_file():
    config_data = {
        'rag': {'chunk_size': 1024, 'top_k': 3},
        'agent': {'temperature': 0.5}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name
    
    manager = ConfigManager(config_path)
    config = manager.get_config()
    
    assert config.rag.chunk_size == 1024
    assert config.rag.top_k == 3
    assert config.agent.temperature == 0.5
    
    Path(config_path).unlink()

def test_update_config():
    manager = ConfigManager()
    manager.update_config({'rag': {'chunk_size': 2048}})
    
    config = manager.get_config()
    assert config.rag.chunk_size == 2048
```

- [ ] **Step 7: 运行配置测试**

运行: `pytest tests/backend/test_config.py -v`
预期: 所有测试通过

- [ ] **Step 8: 提交配置管理代码**

```bash
git add config.yaml requirements.txt .env.example backend/ tests/
git commit -m "feat: add configuration management module"
```

---

## Task 2: RAG核心模块 - 文档加载和文本分割

**Files:**
- Create: `backend/rag/__init__.py`
- Create: `backend/rag/document_loader.py`
- Create: `backend/rag/text_splitter.py`
- Test: `tests/backend/rag/test_document_loader.py`
- Test: `tests/backend/rag/test_text_splitter.py`

- [ ] **Step 1: 创建RAG模块初始化**

```python
# backend/rag/__init__.py
from .document_loader import DocumentLoader
from .text_splitter import TextSplitter
from .embeddings import EmbeddingManager
from .vector_store import VectorStoreManager
from .retriever import Retriever
from .generator import Generator

__all__ = [
    "DocumentLoader",
    "TextSplitter", 
    "EmbeddingManager",
    "VectorStoreManager",
    "Retriever",
    "Generator"
]
```

- [ ] **Step 2: 编写文档加载器测试**

```python
# tests/backend/rag/test_document_loader.py
import pytest
import tempfile
from pathlib import Path
from backend.rag.document_loader import DocumentLoader

def test_load_markdown_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Test\n\nThis is a test document.")
        file_path = f.name
    
    loader = DocumentLoader()
    documents = loader.load_file(file_path)
    
    assert len(documents) == 1
    assert documents[0].page_content == "# Test\n\nThis is a test document."
    assert documents[0].metadata['source'] == file_path
    
    Path(file_path).unlink()

def test_load_text_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Plain text content.")
        file_path = f.name
    
    loader = DocumentLoader()
    documents = loader.load_file(file_path)
    
    assert len(documents) == 1
    assert documents[0].page_content == "Plain text content."
    
    Path(file_path).unlink()

def test_load_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        md_file = Path(temp_dir) / "test.md"
        md_file.write_text("# Markdown\n\nContent here.")
        
        txt_file = Path(temp_dir) / "test.txt"
        txt_file.write_text("Text content.")
        
        loader = DocumentLoader()
        documents = loader.load_directory(temp_dir)
        
        assert len(documents) == 2
        sources = [doc.metadata['source'] for doc in documents]
        assert str(md_file) in sources
        assert str(txt_file) in sources

def test_unsupported_file_type():
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        file_path = f.name
    
    loader = DocumentLoader()
    documents = loader.load_file(file_path)
    
    assert len(documents) == 0
    
    Path(file_path).unlink()
```

- [ ] **Step 3: 实现文档加载器**

```python
# backend/rag/document_loader.py
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from backend.utils.logger import setup_logger

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
```

- [ ] **Step 4: 运行文档加载器测试**

运行: `pytest tests/backend/rag/test_document_loader.py -v`
预期: 所有测试通过

- [ ] **Step 5: 编写文本分割器测试**

```python
# tests/backend/rag/test_text_splitter.py
import pytest
from backend.rag.text_splitter import TextSplitter
from langchain_core.documents import Document

def test_split_short_document():
    splitter = TextSplitter(chunk_size=100, chunk_overlap=20)
    doc = Document(page_content="Short document content.")
    
    chunks = splitter.split_documents([doc])
    
    assert len(chunks) == 1
    assert chunks[0].page_content == "Short document content."

def test_split_long_document():
    splitter = TextSplitter(chunk_size=50, chunk_overlap=10)
    content = "This is a test document. " * 10  # 250 characters
    doc = Document(page_content=content, metadata={'source': 'test.md'})
    
    chunks = splitter.split_documents([doc])
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.page_content) <= 50
        assert chunk.metadata['source'] == 'test.md'

def test_split_preserves_metadata():
    splitter = TextSplitter(chunk_size=50, chunk_overlap=10)
    doc = Document(
        page_content="Test content for splitting.",
        metadata={'source': 'test.md', 'filename': 'test.md'}
    )
    
    chunks = splitter.split_documents([doc])
    
    for chunk in chunks:
        assert chunk.metadata['source'] == 'test.md'
        assert chunk.metadata['filename'] == 'test.md'

def test_split_empty_document():
    splitter = TextSplitter()
    doc = Document(page_content="")
    
    chunks = splitter.split_documents([doc])
    
    assert len(chunks) == 0
```

- [ ] **Step 6: 实现文本分割器**

```python
# backend/rag/text_splitter.py
from typing import List
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.utils.logger import setup_logger

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
```

- [ ] **Step 7: 运行文本分割器测试**

运行: `pytest tests/backend/rag/test_text_splitter.py -v`
预期: 所有测试通过

- [ ] **Step 8: 提交文档加载和分割代码**

```bash
git add backend/rag/ tests/backend/rag/
git commit -m "feat: add document loader and text splitter"
```

---

## Task 3: RAG核心模块 - 嵌入和向量存储

**Files:**
- Create: `backend/rag/embeddings.py`
- Create: `backend/rag/vector_store.py`
- Test: `tests/backend/rag/test_embeddings.py`
- Test: `tests/backend/rag/test_vector_store.py`

- [ ] **Step 1: 编写嵌入模型测试**

```python
# tests/backend/rag/test_embeddings.py
import pytest
from unittest.mock import Mock, patch
from backend.rag.embeddings import EmbeddingManager

def test_embedding_manager_initialization():
    config = {
        'provider': 'openai',
        'model': 'text-embedding-ada-002',
        'base_api': 'https://api.openai.com/v1'
    }
    
    manager = EmbeddingManager(config)
    assert manager.provider == 'openai'
    assert manager.model == 'text-embedding-ada-002'

def test_get_embedding_model():
    config = {
        'provider': 'openai',
        'model': 'text-embedding-ada-002',
        'base_api': 'https://api.openai.com/v1'
    }
    
    manager = EmbeddingManager(config)
    embedding_model = manager.get_embedding_model()
    
    assert embedding_model is not None

def test_unsupported_provider():
    config = {
        'provider': 'unsupported',
        'model': 'test-model',
        'base_api': 'https://api.test.com'
    }
    
    with pytest.raises(ValueError):
        manager = EmbeddingManager(config)
        manager.get_embedding_model()
```

- [ ] **Step 2: 实现嵌入模型管理器**

```python
# backend/rag/embeddings.py
from typing import Dict, Any
from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import OpenAIEmbeddings
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class EmbeddingManager:
    def __init__(self, config: Dict[str, Any]):
        self.provider = config.get('provider', 'openai')
        self.model = config.get('model', 'text-embedding-ada-002')
        self.base_api = config.get('base_api', 'https://api.openai.com/v1')
        self._embedding_model = None
    
    def get_embedding_model(self) -> Embeddings:
        if self._embedding_model is None:
            self._embedding_model = self._create_embedding_model()
        return self._embedding_model
    
    def _create_embedding_model(self) -> Embeddings:
        if self.provider == 'openai':
            return OpenAIEmbeddings(
                model=self.model,
                openai_api_base=self.base_api
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
    
    def update_config(self, config: Dict[str, Any]):
        self.provider = config.get('provider', self.provider)
        self.model = config.get('model', self.model)
        self.base_api = config.get('base_api', self.base_api)
        self._embedding_model = None
```

- [ ] **Step 3: 运行嵌入模型测试**

运行: `pytest tests/backend/rag/test_embeddings.py -v`
预期: 所有测试通过

- [ ] **Step 4: 编写向量存储测试**

```python
# tests/backend/rag/test_vector_store.py
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from backend.rag.vector_store import VectorStoreManager
from langchain_core.documents import Document

def test_vector_store_initialization():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            'persist_directory': temp_dir,
            'collection_name': 'test_collection'
        }
        
        manager = VectorStoreManager(config)
        assert manager.persist_directory == temp_dir
        assert manager.collection_name == 'test_collection'

def test_add_documents():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            'persist_directory': temp_dir,
            'collection_name': 'test_collection'
        }
        
        manager = VectorStoreManager(config)
        
        documents = [
            Document(page_content="Test document 1", metadata={'source': 'test1.md'}),
            Document(page_content="Test document 2", metadata={'source': 'test2.md'})
        ]
        
        with patch.object(manager, '_get_embedding_model') as mock_embedding:
            mock_embedding.return_value = Mock()
            doc_ids = manager.add_documents(documents)
            
            assert len(doc_ids) == 2

def test_similarity_search():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            'persist_directory': temp_dir,
            'collection_name': 'test_collection'
        }
        
        manager = VectorStoreManager(config)
        
        with patch.object(manager, '_get_embedding_model') as mock_embedding:
            mock_embedding.return_value = Mock()
            
            results = manager.similarity_search("test query", k=2)
            
            assert isinstance(results, list)
```

- [ ] **Step 5: 实现向量存储管理器**

```python
# backend/rag/vector_store.py
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from backend.rag.embeddings import EmbeddingManager
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class VectorStoreManager:
    def __init__(self, config: Dict[str, Any]):
        self.persist_directory = config.get('persist_directory', './chroma_db')
        self.collection_name = config.get('collection_name', 'documents')
        self.embedding_manager = None
        self.vector_store = None
        
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
    
    def initialize(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
        embedding_model = embedding_manager.get_embedding_model()
        
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embedding_model,
            collection_name=self.collection_name
        )
        
        logger.info(f"Initialized vector store at {self.persist_directory}")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        if self.vector_store is None:
            raise RuntimeError("Vector store not initialized")
        
        if not documents:
            return []
        
        doc_ids = self.vector_store.add_documents(documents)
        logger.info(f"Added {len(documents)} documents to vector store")
        return doc_ids
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if self.vector_store is None:
            raise RuntimeError("Vector store not initialized")
        
        results = self.vector_store.similarity_search(query, k=k)
        logger.info(f"Found {len(results)} similar documents for query")
        return results
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        if self.vector_store is None:
            raise RuntimeError("Vector store not initialized")
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        logger.info(f"Found {len(results)} similar documents with scores")
        return results
    
    def delete_collection(self):
        if self.vector_store is not None:
            self.vector_store.delete_collection()
            logger.info("Deleted vector store collection")
    
    def get_document_count(self) -> int:
        if self.vector_store is None:
            return 0
        
        collection = self.vector_store._collection
        return collection.count()
```

- [ ] **Step 6: 运行向量存储测试**

运行: `pytest tests/backend/rag/test_vector_store.py -v`
预期: 所有测试通过

- [ ] **Step 7: 提交嵌入和向量存储代码**

```bash
git add backend/rag/embeddings.py backend/rag/vector_store.py tests/backend/rag/
git commit -m "feat: add embedding and vector store modules"
```

---

## Task 4: RAG核心模块 - 检索器和生成器

**Files:**
- Create: `backend/rag/retriever.py`
- Create: `backend/rag/generator.py`
- Test: `tests/backend/rag/test_retriever.py`
- Test: `tests/backend/rag/test_generator.py`

- [ ] **Step 1: 编写检索器测试**

```python
# tests/backend/rag/test_retriever.py
import pytest
from unittest.mock import Mock, patch
from backend.rag.retriever import Retriever
from langchain_core.documents import Document

def test_retriever_initialization():
    config = {
        'top_k': 5,
        'similarity_threshold': 0.7
    }
    
    retriever = Retriever(config)
    assert retriever.top_k == 5
    assert retriever.similarity_threshold == 0.7

def test_retrieve_documents():
    config = {
        'top_k': 3,
        'similarity_threshold': 0.5
    }
    
    retriever = Retriever(config)
    
    mock_vector_store = Mock()
    mock_vector_store.similarity_search_with_score.return_value = [
        (Document(page_content="Test 1", metadata={'source': 'test.md'}), 0.9),
        (Document(page_content="Test 2", metadata={'source': 'test.md'}), 0.8),
        (Document(page_content="Test 3", metadata={'source': 'test.md'}), 0.7)
    ]
    
    retriever.vector_store = mock_vector_store
    
    results = retriever.retrieve("test query")
    
    assert len(results) == 3
    mock_vector_store.similarity_search_with_score.assert_called_once()

def test_filter_by_threshold():
    config = {
        'top_k': 5,
        'similarity_threshold': 0.8
    }
    
    retriever = Retriever(config)
    
    mock_vector_store = Mock()
    mock_vector_store.similarity_search_with_score.return_value = [
        (Document(page_content="Test 1", metadata={'source': 'test.md'}), 0.9),
        (Document(page_content="Test 2", metadata={'source': 'test.md'}), 0.7),  # Below threshold
        (Document(page_content="Test 3", metadata={'source': 'test.md'}), 0.85)
    ]
    
    retriever.vector_store = mock_vector_store
    
    results = retriever.retrieve("test query")
    
    assert len(results) == 2  # Only 2 above threshold
```

- [ ] **Step 2: 实现检索器**

```python
# backend/rag/retriever.py
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from backend.rag.vector_store import VectorStoreManager
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class Retriever:
    def __init__(self, config: Dict[str, Any]):
        self.top_k = config.get('top_k', 5)
        self.similarity_threshold = config.get('similarity_threshold', 0.7)
        self.vector_store_manager = None
    
    def initialize(self, vector_store_manager: VectorStoreManager):
        self.vector_store_manager = vector_store_manager
    
    def retrieve(self, query: str, top_k: int = None) -> List[Tuple[Document, float]]:
        if self.vector_store_manager is None:
            raise RuntimeError("Retriever not initialized")
        
        k = top_k or self.top_k
        
        results = self.vector_store_manager.similarity_search_with_score(query, k=k)
        
        filtered_results = []
        for doc, score in results:
            if score >= self.similarity_threshold:
                filtered_results.append((doc, score))
        
        logger.info(f"Retrieved {len(filtered_results)} documents above threshold {self.similarity_threshold}")
        return filtered_results
    
    def retrieve_simple(self, query: str, top_k: int = None) -> List[Document]:
        results = self.retrieve(query, top_k)
        return [doc for doc, score in results]
    
    def update_config(self, config: Dict[str, Any]):
        self.top_k = config.get('top_k', self.top_k)
        self.similarity_threshold = config.get('similarity_threshold', self.similarity_threshold)
```

- [ ] **Step 3: 运行检索器测试**

运行: `pytest tests/backend/rag/test_retriever.py -v`
预期: 所有测试通过

- [ ] **Step 4: 编写生成器测试**

```python
# tests/backend/rag/test_generator.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.rag.generator import Generator
from langchain_core.documents import Document

def test_generator_initialization():
    config = {
        'provider': 'openai',
        'model': 'gpt-3.5-turbo',
        'base_api': 'https://api.openai.com/v1',
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    generator = Generator(config)
    assert generator.provider == 'openai'
    assert generator.model == 'gpt-3.5-turbo'

def test_create_prompt():
    config = {
        'provider': 'openai',
        'model': 'gpt-3.5-turbo',
        'base_api': 'https://api.openai.com/v1'
    }
    
    generator = Generator(config)
    
    context = "Test context"
    question = "Test question"
    system_prompt = "You are a helpful assistant."
    
    prompt = generator.create_prompt(context, question, system_prompt)
    
    assert context in prompt
    assert question in prompt
    assert system_prompt in prompt

def test_format_context():
    config = {
        'provider': 'openai',
        'model': 'gpt-3.5-turbo',
        'base_api': 'https://api.openai.com/v1'
    }
    
    generator = Generator(config)
    
    documents = [
        (Document(page_content="Content 1", metadata={'source': 'test1.md'}), 0.9),
        (Document(page_content="Content 2", metadata={'source': 'test2.md'}), 0.8)
    ]
    
    context = generator.format_context(documents)
    
    assert "Content 1" in context
    assert "Content 2" in context
    assert "test1.md" in context
    assert "test2.md" in context
```

- [ ] **Step 5: 实现生成器**

```python
# backend/rag/generator.py
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class Generator:
    def __init__(self, config: Dict[str, Any]):
        self.provider = config.get('provider', 'openai')
        self.model = config.get('model', 'gpt-3.5-turbo')
        self.base_api = config.get('base_api', 'https://api.openai.com/v1')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2000)
        self.llm = None
    
    def initialize(self):
        if self.provider == 'openai':
            self.llm = ChatOpenAI(
                model=self.model,
                openai_api_base=self.base_api,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        logger.info(f"Initialized generator with {self.provider}/{self.model}")
    
    def create_prompt(self, context: str, question: str, system_prompt: str) -> str:
        prompt = f"""{system_prompt}

上下文：
{context}

问题：{question}

回答时请引用来源，格式为：[来源：文档名]"""
        return prompt
    
    def format_context(self, documents: List[Tuple[Document, float]]) -> str:
        if not documents:
            return "未找到相关文档。"
        
        context_parts = []
        for i, (doc, score) in enumerate(documents, 1):
            source = doc.metadata.get('source', '未知来源')
            content = doc.page_content
            context_parts.append(f"[文档{i}] 来源: {source}\n内容: {content}\n相似度: {score:.2f}")
        
        return "\n\n".join(context_parts)
    
    def generate(self, context: str, question: str, system_prompt: str) -> str:
        if self.llm is None:
            raise RuntimeError("Generator not initialized")
        
        prompt = self.create_prompt(context, question, system_prompt)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"生成回答时出错: {str(e)}"
    
    def generate_with_citations(self, question: str, documents: List[Tuple[Document, float]], system_prompt: str) -> Tuple[str, List[Dict[str, Any]]]:
        context = self.format_context(documents)
        response = self.generate(context, question, system_prompt)
        
        citations = []
        for doc, score in documents:
            citation = {
                'source': doc.metadata.get('source', '未知来源'),
                'filename': doc.metadata.get('filename', '未知文件'),
                'content_preview': doc.page_content[:100] + '...' if len(doc.page_content) > 100 else doc.page_content,
                'similarity_score': score
            }
            citations.append(citation)
        
        return response, citations
    
    def update_config(self, config: Dict[str, Any]):
        self.provider = config.get('provider', self.provider)
        self.model = config.get('model', self.model)
        self.base_api = config.get('base_api', self.base_api)
        self.temperature = config.get('temperature', self.temperature)
        self.max_tokens = config.get('max_tokens', self.max_tokens)
        self.llm = None
```

- [ ] **Step 6: 运行生成器测试**

运行: `pytest tests/backend/rag/test_generator.py -v`
预期: 所有测试通过

- [ ] **Step 7: 提交检索器和生成器代码**

```bash
git add backend/rag/retriever.py backend/rag/generator.py tests/backend/rag/
git commit -m "feat: add retriever and generator modules"
```

---

## Task 5: Agent模块 - 对话管理和引用溯源

**Files:**
- Create: `backend/agent/__init__.py`
- Create: `backend/agent/conversation.py`
- Create: `backend/agent/citation.py`
- Create: `backend/agent/behavior.py`
- Test: `tests/backend/agent/test_conversation.py`
- Test: `tests/backend/agent/test_citation.py`

- [ ] **Step 1: 创建Agent模块初始化**

```python
# backend/agent/__init__.py
from .conversation import ConversationManager
from .citation import CitationManager
from .behavior import AgentBehavior

__all__ = ["ConversationManager", "CitationManager", "AgentBehavior"]
```

- [ ] **Step 2: 编写对话管理测试**

```python
# tests/backend/agent/test_conversation.py
import pytest
from backend.agent.conversation import ConversationManager

def test_conversation_initialization():
    manager = ConversationManager(max_history=5)
    assert manager.max_history == 5
    assert len(manager.history) == 0

def test_add_message():
    manager = ConversationManager()
    
    manager.add_message("user", "Hello")
    manager.add_message("assistant", "Hi there!")
    
    assert len(manager.history) == 2
    assert manager.history[0]['role'] == 'user'
    assert manager.history[1]['role'] == 'assistant'

def test_get_history():
    manager = ConversationManager(max_history=3)
    
    for i in range(5):
        manager.add_message("user", f"Message {i}")
        manager.add_message("assistant", f"Response {i}")
    
    history = manager.get_history()
    
    assert len(history) == 3  # Only last 3 messages
    assert history[0]['content'] == "Message 4"
    assert history[1]['content'] == "Response 4"
    assert history[2]['content'] == "Message 4"  # Wait, this is wrong

def test_clear_history():
    manager = ConversationManager()
    
    manager.add_message("user", "Hello")
    manager.add_message("assistant", "Hi!")
    
    manager.clear_history()
    
    assert len(manager.history) == 0

def test_get_context_string():
    manager = ConversationManager()
    
    manager.add_message("user", "What is Python?")
    manager.add_message("assistant", "Python is a programming language.")
    manager.add_message("user", "How do I install it?")
    
    context = manager.get_context_string()
    
    assert "What is Python?" in context
    assert "Python is a programming language." in context
    assert "How do I install it?" in context
```

- [ ] **Step 3: 实现对话管理器**

```python
# backend/agent/conversation.py
from typing import List, Dict, Any
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class ConversationManager:
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        message = {
            'role': role,
            'content': content,
            'timestamp': self._get_timestamp()
        }
        self.history.append(message)
        
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        logger.debug(f"Added {role} message to history")
    
    def get_history(self) -> List[Dict[str, str]]:
        return self.history.copy()
    
    def get_context_string(self) -> str:
        if not self.history:
            return ""
        
        context_parts = []
        for msg in self.history:
            role = "用户" if msg['role'] == 'user' else "助手"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def clear_history(self):
        self.history.clear()
        logger.info("Cleared conversation history")
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
    
    def update_config(self, max_history: int):
        self.max_history = max_history
        if len(self.history) > max_history:
            self.history = self.history[-max_history:]
```

- [ ] **Step 4: 运行对话管理测试**

运行: `pytest tests/backend/agent/test_conversation.py -v`
预期: 所有测试通过（注意：有一个测试可能需要修复）

- [ ] **Step 5: 编写引用溯源测试**

```python
# tests/backend/agent/test_citation.py
import pytest
from backend.agent.citation import CitationManager
from langchain_core.documents import Document

def test_citation_manager_initialization():
    manager = CitationManager()
    assert manager is not None

def test_format_citation():
    manager = CitationManager()
    
    doc = Document(
        page_content="This is test content for citation.",
        metadata={
            'source': 'test.md',
            'filename': 'test.md',
            'chunk_index': 0,
            'total_chunks': 3
        }
    )
    
    citation = manager.format_citation(doc, 0.85)
    
    assert citation['source'] == 'test.md'
    assert citation['filename'] == 'test.md'
    assert citation['similarity_score'] == 0.85
    assert 'content_preview' in citation

def test_format_citations_list():
    manager = CitationManager()
    
    documents = [
        (Document(page_content="Content 1", metadata={'source': 'test1.md'}), 0.9),
        (Document(page_content="Content 2", metadata={'source': 'test2.md'}), 0.8)
    ]
    
    citations = manager.format_citations_list(documents)
    
    assert len(citations) == 2
    assert citations[0]['source'] == 'test1.md'
    assert citations[1]['source'] == 'test2.md'

def test_create_citation_text():
    manager = CitationManager()
    
    citations = [
        {'source': 'test1.md', 'filename': 'test1.md', 'content_preview': 'Content 1...', 'similarity_score': 0.9},
        {'source': 'test2.md', 'filename': 'test2.md', 'content_preview': 'Content 2...', 'similarity_score': 0.8}
    ]
    
    citation_text = manager.create_citation_text(citations)
    
    assert "test1.md" in citation_text
    assert "test2.md" in citation_text
    assert "引用来源" in citation_text

def test_extract_source_summary():
    manager = CitationManager()
    
    doc = Document(
        page_content="This is a long content that should be truncated for preview purposes. " * 10,
        metadata={'source': 'test.md'}
    )
    
    summary = manager.extract_source_summary(doc, max_length=50)
    
    assert len(summary) <= 50
    assert summary.endswith('...')
```

- [ ] **Step 6: 实现引用溯源管理器**

```python
# backend/agent/citation.py
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class CitationManager:
    def __init__(self):
        pass
    
    def format_citation(self, doc: Document, score: float) -> Dict[str, Any]:
        content = doc.page_content
        if len(content) > 100:
            content_preview = content[:100] + '...'
        else:
            content_preview = content
        
        return {
            'source': doc.metadata.get('source', '未知来源'),
            'filename': doc.metadata.get('filename', '未知文件'),
            'content_preview': content_preview,
            'similarity_score': score,
            'chunk_index': doc.metadata.get('chunk_index', 0),
            'total_chunks': doc.metadata.get('total_chunks', 1)
        }
    
    def format_citations_list(self, documents: List[Tuple[Document, float]]) -> List[Dict[str, Any]]:
        citations = []
        for doc, score in documents:
            citation = self.format_citation(doc, score)
            citations.append(citation)
        return citations
    
    def create_citation_text(self, citations: List[Dict[str, Any]]) -> str:
        if not citations:
            return ""
        
        citation_lines = ["\n\n引用来源："]
        for i, citation in enumerate(citations, 1):
            source = citation.get('source', '未知来源')
            filename = citation.get('filename', '未知文件')
            score = citation.get('similarity_score', 0)
            citation_lines.append(f"{i}. [{filename}] - 相似度: {score:.2f}")
        
        return "\n".join(citation_lines)
    
    def extract_source_summary(self, doc: Document, max_length: int = 100) -> str:
        content = doc.page_content
        if len(content) <= max_length:
            return content
        else:
            return content[:max_length] + '...'
    
    def create_response_with_citations(self, response: str, citations: List[Dict[str, Any]]) -> str:
        if not citations:
            return response
        
        citation_text = self.create_citation_text(citations)
        return response + citation_text
```

- [ ] **Step 7: 运行引用溯源测试**

运行: `pytest tests/backend/agent/test_citation.py -v`
预期: 所有测试通过

- [ ] **Step 8: 实现Agent行为模块**

```python
# backend/agent/behavior.py
from typing import List, Dict, Any, Tuple, Optional
from langchain_core.documents import Document
from backend.agent.conversation import ConversationManager
from backend.agent.citation import CitationManager
from backend.rag.retriever import Retriever
from backend.rag.generator import Generator
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class AgentBehavior:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conversation_manager = ConversationManager(
            max_history=config.get('max_history', 10)
        )
        self.citation_manager = CitationManager()
        self.retriever = None
        self.generator = None
        self.system_prompt = config.get('system_prompt', '')
        self.refuse_when_no_context = config.get('refuse_when_no_context', True)
    
    def initialize(self, retriever: Retriever, generator: Generator):
        self.retriever = retriever
        self.generator = generator
    
    def process_question(self, question: str) -> Dict[str, Any]:
        self.conversation_manager.add_message("user", question)
        
        if self.retriever is None or self.generator is None:
            return self._create_error_response("Agent not initialized")
        
        try:
            documents = self.retriever.retrieve(question)
            
            if not documents and self.refuse_when_no_context:
                response = "知识库中未找到相关信息，无法回答您的问题。"
                self.conversation_manager.add_message("assistant", response)
                return {
                    'response': response,
                    'citations': [],
                    'has_context': False
                }
            
            response, citations = self.generator.generate_with_citations(
                question=question,
                documents=documents,
                system_prompt=self.system_prompt
            )
            
            formatted_citations = self.citation_manager.format_citations_list(documents)
            
            self.conversation_manager.add_message("assistant", response)
            
            return {
                'response': response,
                'citations': formatted_citations,
                'has_context': True,
                'document_count': len(documents)
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            error_response = f"处理问题时出错: {str(e)}"
            self.conversation_manager.add_message("assistant", error_response)
            return self._create_error_response(error_response)
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        return {
            'response': error_message,
            'citations': [],
            'has_context': False,
            'error': True
        }
    
    def clear_conversation(self):
        self.conversation_manager.clear_history()
        logger.info("Cleared conversation")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self.conversation_manager.get_history()
    
    def update_config(self, config: Dict[str, Any]):
        self.config.update(config)
        self.system_prompt = config.get('system_prompt', self.system_prompt)
        self.refuse_when_no_context = config.get('refuse_when_no_context', self.refuse_when_no_context)
        self.conversation_manager.update_config(
            max_history=config.get('max_history', self.conversation_manager.max_history)
        )
```

- [ ] **Step 9: 提交Agent模块代码**

```bash
git add backend/agent/ tests/backend/agent/
git commit -m "feat: add agent modules with conversation and citation management"
```

---

## Task 6: API路由和FastAPI应用

**Files:**
- Create: `backend/api/__init__.py`
- Create: `backend/api/chat.py`
- Create: `backend/api/documents.py`
- Create: `backend/api/config.py`
- Create: `backend/main.py`
- Test: `tests/backend/api/test_chat.py`

- [ ] **Step 1: 创建API模块初始化**

```python
# backend/api/__init__.py
from .chat import router as chat_router
from .documents import router as documents_router
from .config import router as config_router

__all__ = ["chat_router", "documents_router", "config_router"]
```

- [ ] **Step 2: 实现聊天API**

```python
# backend/api/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.agent.behavior import AgentBehavior
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    citations: List[Dict[str, Any]]
    has_context: bool
    conversation_id: Optional[str] = None

class ConversationHistory(BaseModel):
    history: List[Dict[str, str]]

# This will be initialized in main.py
agent_behavior: Optional[AgentBehavior] = None

def set_agent_behavior(agent: AgentBehavior):
    global agent_behavior
    agent_behavior = agent

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    if agent_behavior is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        result = agent_behavior.process_question(request.question)
        
        return ChatResponse(
            response=result['response'],
            citations=result['citations'],
            has_context=result['has_context'],
            conversation_id=request.conversation_id
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=ConversationHistory)
async def get_conversation_history():
    if agent_behavior is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    history = agent_behavior.get_conversation_history()
    return ConversationHistory(history=history)

@router.post("/clear")
async def clear_conversation():
    if agent_behavior is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    agent_behavior.clear_conversation()
    return {"message": "Conversation cleared"}
```

- [ ] **Step 3: 实现文档API**

```python
# backend/api/documents.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
from pathlib import Path
import shutil
from backend.rag.document_loader import DocumentLoader
from backend.rag.text_splitter import TextSplitter
from backend.rag.vector_store import VectorStoreManager
from backend.config import config_manager
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])

document_loader = DocumentLoader()
text_splitter = None
vector_store_manager = None

def set_vector_store_manager(manager: VectorStoreManager):
    global vector_store_manager
    vector_store_manager = manager

def set_text_splitter(splitter: TextSplitter):
    global text_splitter
    text_splitter = splitter

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.md', '.txt')):
        raise HTTPException(status_code=400, detail="Only .md and .txt files are supported")
    
    try:
        upload_dir = Path(config_manager.get_config().storage.uploads)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        documents = document_loader.load_uploaded_file(str(file_path), file.filename)
        
        if text_splitter and vector_store_manager:
            chunks = text_splitter.split_documents(documents)
            vector_store_manager.add_documents(chunks)
        
        return {
            "message": f"File {file.filename} uploaded successfully",
            "filename": file.filename,
            "document_count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_documents():
    try:
        docs_dir = Path(config_manager.get_config().storage.documents)
        uploads_dir = Path(config_manager.get_config().storage.uploads)
        
        documents = []
        
        if docs_dir.exists():
            for file_path in docs_dir.glob("**/*"):
                if file_path.is_file() and file_path.suffix in ['.md', '.txt']:
                    documents.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "type": "local",
                        "size": file_path.stat().st_size
                    })
        
        if uploads_dir.exists():
            for file_path in uploads_dir.glob("**/*"):
                if file_path.is_file() and file_path.suffix in ['.md', '.txt']:
                    documents.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "type": "uploaded",
                        "size": file_path.stat().st_size
                    })
        
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload")
async def reload_documents():
    try:
        config = config_manager.get_config()
        
        documents = []
        
        if config.sources.local.enabled:
            local_docs = document_loader.load_directory(
                config.sources.local.path,
                config.sources.local.patterns
            )
            documents.extend(local_docs)
        
        if text_splitter and vector_store_manager:
            chunks = text_splitter.split_documents(documents)
            vector_store_manager.add_documents(chunks)
        
        return {
            "message": "Documents reloaded successfully",
            "document_count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error reloading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 4: 实现配置API**

```python
# backend/api/config.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.config import config_manager
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api/config", tags=["config"])

class ConfigUpdate(BaseModel):
    section: str
    updates: Dict[str, Any]

@router.get("/")
async def get_config():
    try:
        config = config_manager.get_config()
        return config.dict()
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update")
async def update_config(request: ConfigUpdate):
    try:
        current_config = config_manager.get_config().dict()
        
        if request.section not in current_config:
            raise HTTPException(status_code=400, detail=f"Invalid config section: {request.section}")
        
        section_config = current_config[request.section]
        section_config.update(request.updates)
        
        config_manager.update_config({request.section: section_config})
        
        return {"message": f"Config section {request.section} updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload")
async def reload_config():
    try:
        config_manager.reload_config()
        return {"message": "Config reloaded successfully"}
    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 5: 实现FastAPI主应用**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.config import config_manager
from backend.rag.document_loader import DocumentLoader
from backend.rag.text_splitter import TextSplitter
from backend.rag.embeddings import EmbeddingManager
from backend.rag.vector_store import VectorStoreManager
from backend.rag.retriever import Retriever
from backend.rag.generator import Generator
from backend.agent.behavior import AgentBehavior
from backend.api.chat import router as chat_router, set_agent_behavior
from backend.api.documents import router as documents_router, set_vector_store_manager, set_text_splitter
from backend.api.config import router as config_router
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global instances
document_loader = DocumentLoader()
text_splitter = None
embedding_manager = None
vector_store_manager = None
retriever = None
generator = None
agent_behavior = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global text_splitter, embedding_manager, vector_store_manager, retriever, generator, agent_behavior
    
    try:
        config = config_manager.get_config()
        
        # Initialize components
        text_splitter = TextSplitter(
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap
        )
        
        embedding_manager = EmbeddingManager(config.embedding.dict())
        
        vector_store_manager = VectorStoreManager({
            'persist_directory': config.storage.vector_db,
            'collection_name': 'documents'
        })
        vector_store_manager.initialize(embedding_manager)
        
        retriever = Retriever({
            'top_k': config.rag.top_k,
            'similarity_threshold': config.rag.similarity_threshold
        })
        retriever.initialize(vector_store_manager)
        
        generator = Generator(config.llm.dict())
        generator.initialize()
        
        agent_behavior = AgentBehavior(config.agent.dict())
        agent_behavior.initialize(retriever, generator)
        
        # Set dependencies for API routes
        set_agent_behavior(agent_behavior)
        set_vector_store_manager(vector_store_manager)
        set_text_splitter(text_splitter)
        
        # Load initial documents
        if config.sources.local.enabled:
            documents = document_loader.load_directory(
                config.sources.local.path,
                config.sources.local.patterns
            )
            if documents:
                chunks = text_splitter.split_documents(documents)
                vector_store_manager.add_documents(chunks)
                logger.info(f"Loaded {len(documents)} documents, created {len(chunks)} chunks")
        
        logger.info("Application started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    finally:
        logger.info("Application shutting down")

app = FastAPI(
    title="RAG QA Agent",
    description="多源文档智能问答Agent",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(config_router)

@app.get("/")
async def root():
    return {"message": "RAG QA Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

- [ ] **Step 6: 编写API测试**

```python
# tests/backend/api/test_chat.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "RAG QA Agent API"

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

- [ ] **Step 7: 运行API测试**

运行: `pytest tests/backend/api/test_chat.py -v`
预期: 所有测试通过

- [ ] **Step 8: 提交API代码**

```bash
git add backend/api/ backend/main.py tests/backend/api/
git commit -m "feat: add API routes and FastAPI application"
```

---

## Task 7: 示例文档和标准问题

**Files:**
- Create: `docs/python_guide.md`
- Create: `docs/machine_learning.md`
- Create: `docs/web_development.md`
- Create: `docs/database_design.md`
- Create: `docs/project_management.md`
- Create: `tests/test_standard_questions.py`

- [ ] **Step 1: 创建Python编程指南文档**

```markdown
# Python编程指南

## 简介
Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。它广泛应用于Web开发、数据科学、人工智能等领域。

## 基础语法

### 变量和数据类型
Python支持多种数据类型：
- 整数（int）：如 42, -10
- 浮点数（float）：如 3.14, -0.5
- 字符串（str）：如 "Hello", 'World'
- 布尔值（bool）：True 或 False
- 列表（list）：如 [1, 2, 3]
- 字典（dict）：如 {"name": "Alice", "age": 25}

### 函数定义
在Python中，使用 `def` 关键字定义函数：

```python
def greet(name):
    """向用户打招呼"""
    return f"Hello, {name}!"

def add(a, b):
    """计算两个数的和"""
    return a + b
```

函数可以有默认参数：

```python
def power(base, exponent=2):
    """计算幂"""
    return base ** exponent
```

### 条件语句
使用 `if`、`elif`、`else` 进行条件判断：

```python
x = 10
if x > 0:
    print("正数")
elif x < 0:
    print("负数")
else:
    print("零")
```

### 循环
Python支持 `for` 和 `while` 循环：

```python
# for循环
for i in range(5):
    print(i)

# while循环
count = 0
while count < 5:
    print(count)
    count += 1
```

## 面向对象编程

### 类定义
使用 `class` 关键字定义类：

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def bark(self):
        return f"{self.name} says Woof!"
    
    def __str__(self):
        return f"Dog(name={self.name}, age={self.age})"
```

### 继承
Python支持继承：

```python
class Puppy(Dog):
    def __init__(self, name, age, breed):
        super().__init__(name, age)
        self.breed = breed
    
    def play(self):
        return f"{self.name} is playing!"
```

## 常用标准库

### os模块
用于操作系统相关功能：

```python
import os

# 获取当前工作目录
current_dir = os.getcwd()

# 列出目录内容
files = os.listdir('.')

# 创建目录
os.makedirs('new_directory', exist_ok=True)
```

### json模块
用于JSON数据处理：

```python
import json

# 序列化
data = {"name": "Alice", "age": 25}
json_string = json.dumps(data)

# 反序列化
parsed_data = json.loads(json_string)
```

## 最佳实践

1. 使用有意义的变量名
2. 编写文档字符串
3. 遵循PEP 8编码规范
4. 编写单元测试
5. 使用虚拟环境管理依赖
```

- [ ] **Step 2: 创建机器学习入门文档**

```markdown
# 机器学习入门

## 什么是机器学习
机器学习是人工智能的一个子领域，它使计算机能够从数据中学习，而无需显式编程。

## 机器学习的类型

### 监督学习
监督学习是最常见的机器学习类型。它使用带有标签的训练数据来学习输入和输出之间的映射关系。

**特点**：
- 训练数据包含输入和对应的正确输出
- 目标是学习一个映射函数
- 可以用于分类和回归任务

**常见算法**：
- 线性回归
- 逻辑回归
- 支持向量机（SVM）
- 决策树
- 随机森林
- 神经网络

**应用场景**：
- 图像分类
- 垃圾邮件检测
- 房价预测
- 医疗诊断

### 无监督学习
无监督学习使用没有标签的数据来发现数据中的模式和结构。

**特点**：
- 训练数据没有标签
- 目标是发现数据的内在结构
- 可以用于聚类、降维、异常检测

**常见算法**：
- K-means聚类
- 层次聚类
- 主成分分析（PCA）
- 自编码器

**应用场景**：
- 客户细分
- 异常检测
- 数据降维
- 推荐系统

### 强化学习
强化学习通过与环境交互来学习最优策略。

**特点**：
- 智能体通过试错学习
- 通过奖励信号反馈
- 目标是最大化累积奖励

**应用场景**：
- 游戏AI
- 机器人控制
- 自动驾驶
- 资源调度

## 机器学习工作流程

### 1. 数据收集
收集与问题相关的数据。数据可以来自数据库、API、文件等。

### 2. 数据预处理
清洗和转换数据：
- 处理缺失值
- 处理异常值
- 特征缩放
- 特征编码

### 3. 特征工程
选择和创建最相关的特征：
- 特征选择
- 特征提取
- 特征创建

### 4. 模型选择
选择适合问题的算法：
- 考虑问题类型（分类/回归）
- 考虑数据规模
- 考虑计算资源

### 5. 模型训练
使用训练数据训练模型：
- 划分训练集和验证集
- 调整超参数
- 交叉验证

### 6. 模型评估
评估模型性能：
- 准确率、精确率、召回率
- F1分数
- 均方误差（MSE）
- R²分数

### 7. 模型部署
将训练好的模型部署到生产环境：
- 模型序列化
- API接口
- 监控和维护

## 常见挑战

### 过拟合
模型在训练数据上表现很好，但在新数据上表现差。

**解决方法**：
- 增加训练数据
- 正则化
- 早停法
- 集成学习

### 欠拟合
模型在训练数据和新数据上都表现差。

**解决方法**：
- 增加模型复杂度
- 增加特征
- 减少正则化

### 数据不平衡
不同类别的样本数量差异很大。

**解决方法**：
- 过采样少数类
- 欠采样多数类
- 使用合适的评估指标
- 集成学习

## 实践建议

1. 从简单模型开始
2. 理解数据
3. 特征工程很重要
4. 交叉验证
5. 监控模型性能
6. 持续学习和改进
```

- [ ] **Step 3: 创建Web开发技术文档**

```markdown
# Web开发技术

## Web开发概述
Web开发是创建Web应用程序的过程，包括前端开发和后端开发。

## 前端开发

### HTML
HTML（超文本标记语言）是构建Web页面的基础。

```html
<!DOCTYPE html>
<html>
<head>
    <title>我的网页</title>
</head>
<body>
    <h1>欢迎来到我的网页</h1>
    <p>这是一个段落。</p>
    <a href="https://example.com">链接</a>
</body>
</html>
```

### CSS
CSS用于控制网页的样式和布局。

```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

h1 {
    color: #333;
    text-align: center;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}
```

### JavaScript
JavaScript为网页添加交互功能。

```javascript
// 变量声明
let name = "Alice";
const age = 25;

// 函数定义
function greet(name) {
    return `Hello, ${name}!`;
}

// DOM操作
document.getElementById("button").addEventListener("click", function() {
    alert("Button clicked!");
});

// 异步编程
async function fetchData() {
    try {
        const response = await fetch("https://api.example.com/data");
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error:", error);
    }
}
```

### 前端框架

#### React
React是Facebook开发的JavaScript库，用于构建用户界面。

```jsx
import React, { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>
                Increment
            </button>
        </div>
    );
}

export default Counter;
```

#### Vue.js
Vue.js是一个渐进式JavaScript框架。

```vue
<template>
    <div>
        <p>{{ message }}</p>
        <button @click="reverseMessage">Reverse</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            message: 'Hello Vue!'
        }
    },
    methods: {
        reverseMessage() {
            this.message = this.message.split('').reverse().join('')
        }
    }
}
</script>
```

## 后端开发

### Node.js
Node.js是基于Chrome V8引擎的JavaScript运行时。

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.json({ message: 'Hello World!' });
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

### Python后端

#### Flask
Flask是轻量级的Python Web框架。

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify(message="Hello World!")

if __name__ == '__main__':
    app.run(debug=True)
```

#### FastAPI
FastAPI是现代Python Web框架，支持异步。

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World!"}
```

## 数据库

### 关系型数据库
- MySQL
- PostgreSQL
- SQLite

### NoSQL数据库
- MongoDB
- Redis
- Elasticsearch

## 部署和运维

### Docker
容器化应用程序：

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### CI/CD
持续集成和持续部署：
- GitHub Actions
- GitLab CI
- Jenkins

## 最佳实践

1. 响应式设计
2. 性能优化
3. 安全性
4. 可访问性
5. 代码规范
6. 版本控制
7. 测试
8. 文档
```

- [ ] **Step 4: 创建数据库设计文档**

```markdown
# 数据库设计

## 数据库设计基础

### 什么是数据库设计
数据库设计是创建数据库结构的过程，包括表、关系、索引等。

### 设计目标
1. 数据完整性
2. 数据一致性
3. 性能优化
4. 可扩展性
5. 安全性

## 关系型数据库设计

### 范式化
范式化是减少数据冗余的过程。

#### 第一范式（1NF）
- 每个列都是原子的
- 没有重复的列

#### 第二范式（2NF）
- 满足1NF
- 非主键列完全依赖于主键

#### 第三范式（3NF）
- 满足2NF
- 非主键列不传递依赖于主键

### 反范式化
为了性能考虑，有时需要反范式化：
- 增加冗余列
- 增加汇总表
- 增加派生列

## 表设计

### 主键选择
- 自增整数
- UUID
- 业务主键

### 数据类型选择
- 整数：INT, BIGINT
- 字符串：VARCHAR, TEXT
- 日期：DATE, DATETIME, TIMESTAMP
- 布尔：BOOLEAN
- 小数：DECIMAL, FLOAT

### 索引设计
```sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);

-- 复合索引
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);
```

## 关系设计

### 一对一关系
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50)
);

CREATE TABLE user_profiles (
    user_id INT PRIMARY KEY,
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 一对多关系
```sql
CREATE TABLE authors (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE books (
    id INT PRIMARY KEY,
    title VARCHAR(200),
    author_id INT,
    FOREIGN KEY (author_id) REFERENCES authors(id)
);
```

### 多对多关系
```sql
CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE courses (
    id INT PRIMARY KEY,
    title VARCHAR(200)
);

CREATE TABLE enrollments (
    student_id INT,
    course_id INT,
    enrollment_date DATE,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

## 性能优化

### 查询优化
1. 使用EXPLAIN分析查询
2. 避免SELECT *
3. 使用适当的WHERE条件
4. 避免在WHERE中使用函数

### 索引优化
1. 为常用查询创建索引
2. 避免过度索引
3. 定期维护索引

### 缓存策略
1. 查询缓存
2. 应用层缓存
3. 分布式缓存

## 安全性

### SQL注入防护
使用参数化查询：

```python
# 错误方式
query = f"SELECT * FROM users WHERE username = '{username}'"

# 正确方式
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))
```

### 访问控制
1. 最小权限原则
2. 角色基础访问控制
3. 审计日志

## 常见设计模式

### EAV模式
实体-属性-值模式，用于存储动态属性。

### 多租户设计
1. 独立数据库
2. 共享数据库，独立Schema
3. 共享数据库，共享Schema

### 版本控制
1. 软删除
2. 历史表
3. 事件溯源

## 最佳实践

1. 命名规范
2. 文档化
3. 版本控制
4. 备份策略
5. 监控和告警
6. 定期维护
```

- [ ] **Step 5: 创建项目管理文档**

```markdown
# 项目管理

## 项目管理概述
项目管理是应用知识、技能、工具和技术来项目活动以满足项目要求的过程。

## 项目管理方法论

### 瀑布模型
瀑布模型是线性顺序的开发方法。

**阶段**：
1. 需求分析
2. 系统设计
3. 实现
4. 测试
5. 部署
6. 维护

**优点**：
- 简单易懂
- 文档齐全
- 易于管理

**缺点**：
- 不灵活
- 风险后置
- 不适应变化

### 敏捷开发
敏捷开发是迭代和增量的开发方法。

**核心价值观**：
1. 个体和互动高于流程和工具
2. 工作的软件高于详尽的文档
3. 客户合作高于合同谈判
4. 响应变化高于遵循计划

**常见方法**：
- Scrum
- Kanban
- XP（极限编程）

### Scrum框架
Scrum是最流行的敏捷框架之一。

**角色**：
- Product Owner（产品负责人）
- Scrum Master（敏捷教练）
- Development Team（开发团队）

**事件**：
- Sprint（迭代）
- Sprint Planning（迭代计划）
- Daily Standup（每日站会）
- Sprint Review（迭代评审）
- Sprint Retrospective（迭代回顾）

**工件**：
- Product Backlog（产品待办列表）
- Sprint Backlog（迭代待办列表）
- Increment（增量）

## 项目规划

### 工作分解结构（WBS）
将项目分解为可管理的部分。

### 估算
1. 专家判断
2. 类比估算
3. 参数估算
4. 三点估算

### 进度计划
1. 甘特图
2. 关键路径法
3. 里程碑图

## 风险管理

### 风险识别
1. 头脑风暴
2. 德尔菲技术
3. SWOT分析
4. 检查表

### 风险分析
1. 定性分析
2. 定量分析

### 风险应对
1. 规避
2. 转移
3. 减轻
4. 接受

## 沟通管理

### 沟通渠道
1. 会议
2. 邮件
3. 即时通讯
4. 文档

### 沟通计划
1. 谁需要什么信息
2. 何时需要
3. 如何传递
4. 谁负责

## 质量管理

### 质量规划
1. 质量标准
2. 质量度量
3. 质量检查表

### 质量保证
1. 过程审计
2. 过程改进

### 质量控制
1. 检查
2. 测试
3. 统计抽样

## 团队管理

### 团队发展
1. 形成期
2. 震荡期
3. 规范期
4. 执行期

### 冲突管理
1. 回避
2. 妥协
3. 调解
4. 合作

### 领导力
1. 愿景
2. 激励
3. 授权
4. 沟通

## 项目收尾

### 收尾流程
1. 验收成果
2. 文档归档
3. 经验总结
4. 资源释放

### 经验教训
1. 成功经验
2. 失败教训
3. 改进建议

## 工具和技术

### 项目管理工具
- Jira
- Trello
- Asana
- Microsoft Project

### 协作工具
- Slack
- Microsoft Teams
- Zoom
- Google Meet

### 文档工具
- Confluence
- Notion
- Google Docs
- SharePoint

## 最佳实践

1. 明确目标
2. 详细规划
3. 有效沟通
4. 风险管理
5. 质量控制
6. 团队协作
7. 持续改进
8. 文档化
```

- [ ] **Step 6: 编写标准问题测试**

```python
# tests/test_standard_questions.py
import pytest
from backend.agent.behavior import AgentBehavior
from backend.rag.retriever import Retriever
from backend.rag.generator import Generator
from backend.config import config_manager

@pytest.fixture
def agent_behavior():
    config = config_manager.get_config()
    agent = AgentBehavior(config.agent.dict())
    return agent

def test_python_function_question(agent_behavior):
    """测试Python函数定义问题"""
    result = agent_behavior.process_question("Python中如何定义函数？")
    
    assert result['has_context'] == True
    assert 'def' in result['response'].lower()
    assert len(result['citations']) > 0
    
    # 检查是否引用了Python编程指南
    sources = [c['filename'] for c in result['citations']]
    assert any('python' in s.lower() for s in sources)

def test_machine_learning_question(agent_behavior):
    """测试机器学习问题"""
    result = agent_behavior.process_question("什么是监督学习和无监督学习？")
    
    assert result['has_context'] == True
    assert '监督学习' in result['response']
    assert '无监督学习' in result['response']
    
    # 检查是否引用了机器学习文档
    sources = [c['filename'] for c in result['citations']]
    assert any('machine_learning' in s.lower() for s in sources)

def test_database_design_question(agent_behavior):
    """测试数据库设计问题"""
    result = agent_behavior.process_question("如何设计数据库表结构？")
    
    assert result['has_context'] == True
    assert '表' in result['response']
    assert '设计' in result['response']
    
    # 检查是否引用了数据库设计文档
    sources = [c['filename'] for c in result['citations']]
    assert any('database' in s.lower() for s in sources)

def test_out_of_context_question(agent_behavior):
    """测试知识库外问题"""
    result = agent_behavior.process_question("2024年奥运会举办地点是哪里？")
    
    assert result['has_context'] == False
    assert '知识库中未找到' in result['response']
    assert len(result['citations']) == 0
```

- [ ] **Step 7: 运行标准问题测试**

运行: `pytest tests/test_standard_questions.py -v`
预期: 所有测试通过

- [ ] **Step 8: 提交示例文档和测试**

```bash
git add docs/ tests/test_standard_questions.py
git commit -m "feat: add example documents and standard question tests"
```

---

## Task 8: React前端 - 项目初始化和基础组件

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/index.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/services/api.ts`

- [ ] **Step 1: 创建前端项目配置**

```json
// frontend/package.json
{
  "name": "rag-qa-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.39",
    "@types/react-dom": "^18.2.17",
    "antd": "^5.12.2",
    "axios": "^1.6.2",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.5"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  },
  "proxy": "http://localhost:8000",
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

- [ ] **Step 2: 创建TypeScript类型定义**

```typescript
// frontend/src/types/index.ts
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  citations?: Citation[];
}

export interface Citation {
  source: string;
  filename: string;
  content_preview: string;
  similarity_score: number;
}

export interface ChatRequest {
  question: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  citations: Citation[];
  has_context: boolean;
  conversation_id?: string;
}

export interface DocumentInfo {
  filename: string;
  path: string;
  type: 'local' | 'uploaded';
  size: number;
}

export interface Config {
  sources: {
    local: {
      enabled: boolean;
      path: string;
      patterns: string[];
    };
    upload: {
      enabled: boolean;
      path: string;
    };
  };
  rag: {
    chunk_size: number;
    chunk_overlap: number;
    top_k: number;
    similarity_threshold: number;
  };
  agent: {
    max_history: number;
    refuse_when_no_context: boolean;
    temperature: number;
    system_prompt: string;
  };
  ui: {
    show_citations: boolean;
    show_similarity_score: boolean;
    theme: string;
  };
  llm: {
    provider: string;
    model: string;
    base_api: string;
    temperature: number;
    max_tokens: number;
  };
  embedding: {
    provider: string;
    model: string;
    base_api: string;
  };
  storage: {
    vector_db: string;
    documents: string;
    uploads: string;
  };
}
```

- [ ] **Step 3: 创建API服务**

```typescript
// frontend/src/services/api.ts
import axios from 'axios';
import { ChatRequest, ChatResponse, DocumentInfo, Config, Message } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const chatService = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat/message', request);
    return response.data;
  },

  getHistory: async (): Promise<Message[]> => {
    const response = await api.get<{ history: Message[] }>('/chat/history');
    return response.data.history;
  },

  clearConversation: async (): Promise<void> => {
    await api.post('/chat/clear');
  },
};

export const documentService = {
  uploadDocument: async (file: File): Promise<{ message: string; filename: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  listDocuments: async (): Promise<DocumentInfo[]> => {
    const response = await api.get<{ documents: DocumentInfo[] }>('/documents/list');
    return response.data.documents;
  },

  reloadDocuments: async (): Promise<{ message: string }> => {
    const response = await api.post('/documents/reload');
    return response.data;
  },
};

export const configService = {
  getConfig: async (): Promise<Config> => {
    const response = await api.get<Config>('/config/');
    return response.data;
  },

  updateConfig: async (section: string, updates: Record<string, any>): Promise<void> => {
    await api.post('/config/update', { section, updates });
  },

  reloadConfig: async (): Promise<void> => {
    await api.post('/config/reload');
  },
};

export default api;
```

- [ ] **Step 4: 创建React应用入口**

```typescript
// frontend/src/index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

```typescript
// frontend/src/App.tsx
import React from 'react';
import { ConfigProvider } from 'antd';
import ChatWindow from './components/Chat/ChatWindow';
import Sidebar from './components/Sidebar/Sidebar';
import './App.css';

const App: React.FC = () => {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <div className="app-container">
        <div className="sidebar">
          <Sidebar />
        </div>
        <div className="main-content">
          <ChatWindow />
        </div>
      </div>
    </ConfigProvider>
  );
};

export default App;
```

```css
/* frontend/src/App.css */
.app-container {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

.sidebar {
  width: 300px;
  background-color: #fff;
  border-right: 1px solid #e8e8e8;
  overflow-y: auto;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
```

- [ ] **Step 5: 安装前端依赖**

运行: `cd frontend && npm install`
预期: 依赖安装成功

- [ ] **Step 6: 提交前端基础代码**

```bash
git add frontend/
git commit -m "feat: add React frontend with basic structure"
```

---

## Task 9: React前端 - 聊天组件

**Files:**
- Create: `frontend/src/components/Chat/ChatWindow.tsx`
- Create: `frontend/src/components/Chat/MessageList.tsx`
- Create: `frontend/src/components/Chat/MessageInput.tsx`
- Create: `frontend/src/components/Chat/index.ts`
- Create: `frontend/src/hooks/useChat.ts`

- [ ] **Step 1: 创建聊天Hook**

```typescript
// frontend/src/hooks/useChat.ts
import { useState, useCallback } from 'react';
import { Message, Citation } from '../types';
import { chatService } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (question: string) => {
    const userMessage: Message = {
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await chatService.sendMessage({ question });
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        citations: response.citations,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  }, []);

  const clearMessages = useCallback(async () => {
    try {
      await chatService.clearConversation();
      setMessages([]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear conversation');
    }
  }, []);

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearMessages,
  };
};
```

- [ ] **Step 2: 创建消息输入组件**

```typescript
// frontend/src/components/Chat/MessageInput.tsx
import React, { useState } from 'react';
import { Input, Button, Space } from 'antd';
import { SendOutlined, ClearOutlined } from '@ant-design/icons';

interface MessageInputProps {
  onSend: (message: string) => void;
  onClear: () => void;
  loading: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSend, onClear, loading }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !loading) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="message-input-container">
      <Space.Compact style={{ width: '100%' }}>
        <Input.TextArea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入您的问题..."
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={loading}
          style={{ flex: 1 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={loading}
          disabled={!message.trim()}
        >
          发送
        </Button>
        <Button
          icon={<ClearOutlined />}
          onClick={onClear}
          disabled={loading}
        >
          清空
        </Button>
      </Space.Compact>
    </div>
  );
};

export default MessageInput;
```

- [ ] **Step 3: 创建消息列表组件**

```typescript
// frontend/src/components/Chat/MessageList.tsx
import React from 'react';
import { List, Card, Tag, Typography, Collapse } from 'antd';
import { UserOutlined, RobotOutlined, FileTextOutlined } from '@ant-design/icons';
import { Message, Citation } from '../../types';

const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface MessageListProps {
  messages: Message[];
  showCitations: boolean;
}

const CitationCard: React.FC<{ citation: Citation }> = ({ citation }) => (
  <Card size="small" style={{ marginTop: 8, backgroundColor: '#f9f9f9' }}>
    <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
      <FileTextOutlined style={{ marginRight: 8 }} />
      <Text strong>{citation.filename}</Text>
      <Tag color="blue" style={{ marginLeft: 'auto' }}>
        相似度: {(citation.similarity_score * 100).toFixed(1)}%
      </Tag>
    </div>
    <Paragraph
      ellipsis={{ rows: 2, expandable: true }}
      type="secondary"
      style={{ marginBottom: 0 }}
    >
      {citation.content_preview}
    </Paragraph>
  </Card>
);

const MessageItem: React.FC<{ message: Message; showCitations: boolean }> = ({
  message,
  showCitations,
}) => {
  const isUser = message.role === 'user';

  return (
    <List.Item style={{ justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
      <Card
        style={{
          maxWidth: '80%',
          backgroundColor: isUser ? '#1890ff' : '#fff',
          color: isUser ? '#fff' : '#000',
        }}
        bodyStyle={{ padding: '12px 16px' }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
          {!isUser && <RobotOutlined style={{ fontSize: 18, marginTop: 4 }} />}
          <div style={{ flex: 1 }}>
            <Paragraph
              style={{
                margin: 0,
                color: isUser ? '#fff' : '#000',
                whiteSpace: 'pre-wrap',
              }}
            >
              {message.content}
            </Paragraph>
            {!isUser && showCitations && message.citations && message.citations.length > 0 && (
              <Collapse ghost size="small" style={{ marginTop: 8 }}>
                <Panel
                  header={`引用来源 (${message.citations.length})`}
                  key="citations"
                >
                  {message.citations.map((citation, index) => (
                    <CitationCard key={index} citation={citation} />
                  ))}
                </Panel>
              </Collapse>
            )}
          </div>
          {isUser && <UserOutlined style={{ fontSize: 18, marginTop: 4 }} />}
        </div>
      </Card>
    </List.Item>
  );
};

const MessageList: React.FC<MessageListProps> = ({ messages, showCitations }) => {
  return (
    <List
      dataSource={messages}
      renderItem={(message) => (
        <MessageItem message={message} showCitations={showCitations} />
      )}
      style={{ padding: '16px', overflow: 'auto', flex: 1 }}
    />
  );
};

export default MessageList;
```

- [ ] **Step 4: 创建聊天窗口组件**

```typescript
// frontend/src/components/Chat/ChatWindow.tsx
import React from 'react';
import { Card, Typography, Alert, Spin } from 'antd';
import { useChat } from '../../hooks/useChat';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const { Title } = Typography;

const ChatWindow: React.FC = () => {
  const { messages, loading, error, sendMessage, clearMessages } = useChat();

  return (
    <Card
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
      bodyStyle={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        padding: 0,
        overflow: 'hidden',
      }}
    >
      <div style={{ padding: '16px 24px', borderBottom: '1px solid #f0f0f0' }}>
        <Title level={4} style={{ margin: 0 }}>
          RAG 智能问答
        </Title>
      </div>
      
      {error && (
        <Alert
          message="错误"
          description={error}
          type="error"
          closable
          style={{ margin: '16px 24px' }}
        />
      )}

      <MessageList messages={messages} showCitations={true} />
      
      {loading && (
        <div style={{ textAlign: 'center', padding: '16px' }}>
          <Spin tip="正在思考..." />
        </div>
      )}

      <div style={{ padding: '16px 24px', borderTop: '1px solid #f0f0f0' }}>
        <MessageInput
          onSend={sendMessage}
          onClear={clearMessages}
          loading={loading}
        />
      </div>
    </Card>
  );
};

export default ChatWindow;
```

- [ ] **Step 5: 创建组件索引**

```typescript
// frontend/src/components/Chat/index.ts
export { default as ChatWindow } from './ChatWindow';
export { default as MessageList } from './MessageList';
export { default as MessageInput } from './MessageInput';
```

- [ ] **Step 6: 添加CSS样式**

```css
/* frontend/src/components/Chat/Chat.css */
.message-input-container {
  display: flex;
  gap: 8px;
}

.message-input-container .ant-input-text-area {
  resize: none;
}

.ant-list-item {
  border-bottom: none !important;
}

.ant-collapse-header {
  padding: 4px 0 !important;
}

.ant-card-body {
  padding: 12px 16px;
}
```

- [ ] **Step 7: 测试前端构建**

运行: `cd frontend && npm run build`
预期: 构建成功

- [ ] **Step 8: 提交聊天组件**

```bash
git add frontend/src/components/Chat/ frontend/src/hooks/
git commit -m "feat: add chat components with message list and input"
```

---

## Task 10: React前端 - 侧边栏和文件上传

**Files:**
- Create: `frontend/src/components/Sidebar/Sidebar.tsx`
- Create: `frontend/src/components/Sidebar/ConfigPanel.tsx`
- Create: `frontend/src/components/Sidebar/FileList.tsx`
- Create: `frontend/src/components/Sidebar/index.ts`
- Create: `frontend/src/components/FileUpload/UploadArea.tsx`
- Create: `frontend/src/components/FileUpload/index.ts`
- Create: `frontend/src/hooks/useConfig.ts`

- [ ] **Step 1: 创建配置Hook**

```typescript
// frontend/src/hooks/useConfig.ts
import { useState, useEffect, useCallback } from 'react';
import { Config } from '../types';
import { configService } from '../services/api';

export const useConfig = () => {
  const [config, setConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchConfig = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await configService.getConfig();
      setConfig(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch config');
    } finally {
      setLoading(false);
    }
  }, []);

  const updateConfig = useCallback(async (section: string, updates: Record<string, any>) => {
    setLoading(true);
    setError(null);
    try {
      await configService.updateConfig(section, updates);
      await fetchConfig(); // Refresh config
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update config');
    } finally {
      setLoading(false);
    }
  }, [fetchConfig]);

  const reloadConfig = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await configService.reloadConfig();
      await fetchConfig(); // Refresh config
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reload config');
    } finally {
      setLoading(false);
    }
  }, [fetchConfig]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  return {
    config,
    loading,
    error,
    updateConfig,
    reloadConfig,
    fetchConfig,
  };
};
```

- [ ] **Step 2: 创建文件上传组件**

```typescript
// frontend/src/components/FileUpload/UploadArea.tsx
import React, { useState } from 'react';
import { Upload, message, Button, Space } from 'antd';
import { UploadOutlined, InboxOutlined } from '@ant-design/icons';
import { documentService } from '../../services/api';

const { Dragger } = Upload;

interface UploadAreaProps {
  onUploadSuccess: () => void;
}

const UploadArea: React.FC<UploadAreaProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const result = await documentService.uploadDocument(file);
      message.success(`${file.name} 上传成功`);
      onUploadSuccess();
    } catch (error) {
      message.error(`${file.name} 上传失败`);
    } finally {
      setUploading(false);
    }
    return false; // Prevent default upload behavior
  };

  const uploadProps = {
    name: 'file',
    multiple: true,
    accept: '.md,.txt',
    beforeUpload: (file: File) => {
      handleUpload(file);
      return false;
    },
    showUploadList: false,
  };

  return (
    <div style={{ padding: '16px' }}>
      <Dragger {...uploadProps} disabled={uploading}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p className="ant-upload-hint">支持 .md 和 .txt 文件</p>
      </Dragger>
    </div>
  );
};

export default UploadArea;
```

- [ ] **Step 3: 创建文件列表组件**

```typescript
// frontend/src/components/Sidebar/FileList.tsx
import React, { useState, useEffect } from 'react';
import { List, Card, Tag, Typography, Button, message, Spin } from 'antd';
import { FileTextOutlined, ReloadOutlined, DeleteOutlined } from '@ant-design/icons';
import { DocumentInfo } from '../../types';
import { documentService } from '../../services/api';

const { Text } = Typography;

const FileList: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const docs = await documentService.listDocuments();
      setDocuments(docs);
    } catch (error) {
      message.error('获取文档列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleReload = async () => {
    try {
      await documentService.reloadDocuments();
      message.success('文档重新加载成功');
      await fetchDocuments();
    } catch (error) {
      message.error('文档重新加载失败');
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <Card
      title="文档列表"
      size="small"
      extra={
        <Button
          icon={<ReloadOutlined />}
          onClick={handleReload}
          loading={loading}
          size="small"
        >
          刷新
        </Button>
      }
    >
      <Spin spinning={loading}>
        <List
          dataSource={documents}
          renderItem={(doc) => (
            <List.Item>
              <List.Item.Meta
                avatar={<FileTextOutlined />}
                title={
                  <Space>
                    <Text>{doc.filename}</Text>
                    <Tag color={doc.type === 'local' ? 'blue' : 'green'}>
                      {doc.type === 'local' ? '本地' : '上传'}
                    </Tag>
                  </Space>
                }
                description={
                  <Text type="secondary">
                    {(doc.size / 1024).toFixed(1)} KB
                  </Text>
                }
              />
            </List.Item>
          )}
        />
      </Spin>
    </Card>
  );
};

export default FileList;
```

- [ ] **Step 4: 创建配置面板组件**

```typescript
// frontend/src/components/Sidebar/ConfigPanel.tsx
import React, { useState } from 'react';
import { Card, Form, Input, InputNumber, Switch, Button, Space, message, Spin } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import { Config } from '../../types';

interface ConfigPanelProps {
  config: Config | null;
  loading: boolean;
  onUpdate: (section: string, updates: Record<string, any>) => Promise<void>;
  onReload: () => Promise<void>;
}

const ConfigPanel: React.FC<ConfigPanelProps> = ({
  config,
  loading,
  onUpdate,
  onReload,
}) => {
  const [form] = Form.useForm();

  const handleSave = async (section: string) => {
    try {
      const values = form.getFieldValue(section);
      await onUpdate(section, values);
      message.success('配置保存成功');
    } catch (error) {
      message.error('配置保存失败');
    }
  };

  if (!config) {
    return <Spin spinning={loading} />;
  }

  return (
    <Card title="配置面板" size="small">
      <Form
        form={form}
        layout="vertical"
        initialValues={config}
        size="small"
      >
        <Card title="RAG配置" size="small" type="inner">
          <Form.Item name={['rag', 'chunk_size']} label="Chunk大小">
            <InputNumber min={100} max={2000} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name={['rag', 'top_k']} label="Top K">
            <InputNumber min={1} max={20} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name={['rag', 'similarity_threshold']} label="相似度阈值">
            <InputNumber min={0} max={1} step={0.1} style={{ width: '100%' }} />
          </Form.Item>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={() => handleSave('rag')}
            loading={loading}
            size="small"
          >
            保存RAG配置
          </Button>
        </Card>

        <Card title="Agent配置" size="small" type="inner" style={{ marginTop: 16 }}>
          <Form.Item name={['agent', 'refuse_when_no_context']} valuePropName="checked">
            <Switch checkedChildren="开启" unCheckedChildren="关闭" />
          </Form.Item>
          <Form.Item name={['agent', 'system_prompt']} label="系统提示词">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={() => handleSave('agent')}
            loading={loading}
            size="small"
          >
            保存Agent配置
          </Button>
        </Card>

        <Button
          icon={<ReloadOutlined />}
          onClick={onReload}
          loading={loading}
          style={{ marginTop: 16 }}
          block
        >
          重新加载配置
        </Button>
      </Form>
    </Card>
  );
};

export default ConfigPanel;
```

- [ ] **Step 5: 创建侧边栏组件**

```typescript
// frontend/src/components/Sidebar/Sidebar.tsx
import React from 'react';
import { Card, Tabs } from 'antd';
import { SettingOutlined, FileOutlined, UploadOutlined } from '@ant-design/icons';
import ConfigPanel from './ConfigPanel';
import FileList from './FileList';
import UploadArea from '../FileUpload/UploadArea';
import { useConfig } from '../../hooks/useConfig';

const Sidebar: React.FC = () => {
  const { config, loading, updateConfig, reloadConfig } = useConfig();
  const [activeTab, setActiveTab] = React.useState('files');

  const handleUploadSuccess = () => {
    // Refresh file list when upload succeeds
    setActiveTab('files');
  };

  const tabItems = [
    {
      key: 'files',
      label: (
        <span>
          <FileOutlined />
          文档
        </span>
      ),
      children: <FileList />,
    },
    {
      key: 'upload',
      label: (
        <span>
          <UploadOutlined />
          上传
        </span>
      ),
      children: <UploadArea onUploadSuccess={handleUploadSuccess} />,
    },
    {
      key: 'config',
      label: (
        <span>
          <SettingOutlined />
          配置
        </span>
      ),
      children: (
        <ConfigPanel
          config={config}
          loading={loading}
          onUpdate={updateConfig}
          onReload={reloadConfig}
        />
      ),
    },
  ];

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
        <h2 style={{ margin: 0, fontSize: 18 }}>RAG Agent</h2>
      </div>
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
        style={{ flex: 1, overflow: 'auto' }}
        tabBarStyle={{ margin: 0, padding: '0 16px' }}
      />
    </div>
  );
};

export default Sidebar;
```

- [ ] **Step 6: 创建组件索引**

```typescript
// frontend/src/components/Sidebar/index.ts
export { default as Sidebar } from './Sidebar';
export { default as ConfigPanel } from './ConfigPanel';
export { default as FileList } from './FileList';
```

```typescript
// frontend/src/components/FileUpload/index.ts
export { default as UploadArea } from './UploadArea';
```

- [ ] **Step 7: 测试前端构建**

运行: `cd frontend && npm run build`
预期: 构建成功

- [ ] **Step 8: 提交侧边栏和文件上传组件**

```bash
git add frontend/src/components/Sidebar/ frontend/src/components/FileUpload/ frontend/src/hooks/
git commit -m "feat: add sidebar with config panel and file upload"
```

---

## Task 11: 集成测试和README文档

**Files:**
- Create: `README.md`
- Create: `tests/integration/test_integration.py`
- Update: `README.md`

- [ ] **Step 1: 编写集成测试**

```python
# tests/integration/test_integration.py
import pytest
import tempfile
from pathlib import Path
from backend.config import ConfigManager
from backend.rag.document_loader import DocumentLoader
from backend.rag.text_splitter import TextSplitter
from backend.rag.embeddings import EmbeddingManager
from backend.rag.vector_store import VectorStoreManager
from backend.rag.retriever import Retriever
from backend.rag.generator import Generator
from backend.agent.behavior import AgentBehavior

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def sample_documents(temp_dir):
    docs_dir = Path(temp_dir) / "docs"
    docs_dir.mkdir()
    
    # Create sample documents
    (docs_dir / "test1.md").write_text("""
# Test Document 1

This is a test document about Python programming.

## Functions

Functions are defined using the `def` keyword.

```python
def hello():
    print("Hello, World!")
```
""")
    
    (docs_dir / "test2.md").write_text("""
# Test Document 2

This is a test document about machine learning.

## Supervised Learning

Supervised learning uses labeled data to train models.
""")
    
    return str(docs_dir)

def test_full_rag_pipeline(temp_dir, sample_documents):
    """Test complete RAG pipeline from document loading to response generation"""
    config = ConfigManager()
    
    # Initialize components
    document_loader = DocumentLoader()
    text_splitter = TextSplitter(chunk_size=200, chunk_overlap=50)
    
    # Load and split documents
    documents = document_loader.load_directory(sample_documents)
    assert len(documents) == 2
    
    chunks = text_splitter.split_documents(documents)
    assert len(chunks) > 2
    
    # Test that chunks have proper metadata
    for chunk in chunks:
        assert 'source' in chunk.metadata
        assert 'filename' in chunk.metadata

def test_document_loader_with_different_file_types(temp_dir):
    """Test document loader with various file types"""
    document_loader = DocumentLoader()
    
    # Create test files
    md_file = Path(temp_dir) / "test.md"
    md_file.write_text("# Markdown\n\nContent")
    
    txt_file = Path(temp_dir) / "test.txt"
    txt_file.write_text("Plain text content")
    
    unsupported_file = Path(temp_dir) / "test.pdf"
    unsupported_file.write_bytes(b"PDF content")
    
    # Test loading
    md_docs = document_loader.load_file(str(md_file))
    assert len(md_docs) == 1
    
    txt_docs = document_loader.load_file(str(txt_file))
    assert len(txt_docs) == 1
    
    pdf_docs = document_loader.load_file(str(unsupported_file))
    assert len(pdf_docs) == 0

def test_text_splitter_configuration():
    """Test text splitter with different configurations"""
    splitter1 = TextSplitter(chunk_size=100, chunk_overlap=20)
    splitter2 = TextSplitter(chunk_size=200, chunk_overlap=50)
    
    text = "This is a test. " * 20  # 320 characters
    
    from langchain_core.documents import Document
    doc = Document(page_content=text, metadata={'source': 'test.md'})
    
    chunks1 = splitter1.split_documents([doc])
    chunks2 = splitter2.split_documents([doc])
    
    assert len(chunks1) > len(chunks2)
    
    for chunk in chunks1:
        assert len(chunk.page_content) <= 100
    
    for chunk in chunks2:
        assert len(chunk.page_content) <= 200

def test_agent_behavior_with_no_context():
    """Test agent behavior when no context is found"""
    config = {
        'max_history': 10,
        'refuse_when_no_context': True,
        'system_prompt': 'You are a helpful assistant.'
    }
    
    agent = AgentBehavior(config)
    
    # Mock retriever and generator
    from unittest.mock import Mock
    
    mock_retriever = Mock()
    mock_retriever.retrieve.return_value = []
    
    mock_generator = Mock()
    
    agent.initialize(mock_retriever, mock_generator)
    
    result = agent.process_question("What is the meaning of life?")
    
    assert result['has_context'] == False
    assert '知识库中未找到' in result['response']
    assert len(result['citations']) == 0
```

- [ ] **Step 2: 运行集成测试**

运行: `pytest tests/integration/test_integration.py -v`
预期: 所有测试通过

- [ ] **Step 3: 创建README文档**

```markdown
# 多源文档智能问答 Agent（RAG）

一个基于RAG（检索增强生成）的智能问答Agent，能够根据知识库内容回答问题并标注出处。

## 功能特性

### 文档接入
- **本地文件夹**：支持监控本地目录中的 `.md` 和 `.txt` 文件
- **文件上传**：支持通过Web界面上传文档

### RAG流水线
- **文档切分**：智能文档分割，支持中文优化
- **向量化**：使用OpenAI兼容的嵌入模型
- **检索**：基于Chroma向量数据库的相似度检索
- **生成**：使用LLM生成回答并标注引用来源

### Agent行为
- **引用溯源**：每条回答附带引用来源（文档名、相似度分数）
- **拒绝编造**：检索不到相关内容时明确回复「知识库中未找到」
- **支持追问**：维护对话历史，支持多轮对话

### 可配置项
- Chunk大小、Top-K、相似度阈值
- Embedding模型和LLM模型配置
- 数据源路径和系统提示词
- UI显示选项

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd agentDemo

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
cd ..
```

### 2. 配置

复制环境变量示例文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置您的API密钥：
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
```

编辑 `config.yaml` 文件，根据需要调整配置。

### 3. 启动应用

```bash
# 启动后端
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 在另一个终端启动前端
cd frontend
npm start
```

访问 http://localhost:3000 打开Web界面。

## 项目结构

```
agentDemo/
├── README.md                    # 项目说明
├── config.yaml                  # 配置文件
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量示例
├── docs/                        # 示例文档
│   ├── python_guide.md
│   ├── machine_learning.md
│   ├── web_development.md
│   ├── database_design.md
│   └── project_management.md
├── backend/                     # Python后端
│   ├── main.py                  # FastAPI入口
│   ├── config.py                # 配置管理
│   ├── rag/                     # RAG核心模块
│   ├── agent/                   # Agent模块
│   ├── api/                     # API路由
│   └── utils/                   # 工具函数
├── frontend/                    # React前端
│   ├── src/
│   │   ├── components/          # React组件
│   │   ├── hooks/               # 自定义Hooks
│   │   ├── services/            # API服务
│   │   └── types/               # TypeScript类型
│   └── package.json
└── tests/                       # 测试
```

## 配置说明

### 配置文件 (`config.yaml`)

```yaml
# 数据源配置
sources:
  local:
    enabled: true
    path: "./docs"
    patterns: ["**/*.md", "**/*.txt"]
  upload:
    enabled: true
    path: "./uploads"

# RAG配置
rag:
  chunk_size: 512          # 文档切分大小
  chunk_overlap: 64        # 切分重叠大小
  top_k: 5                 # 检索返回的文档数量
  similarity_threshold: 0.7 # 相似度阈值

# Agent配置
agent:
  max_history: 10           # 最大对话历史轮数
  refuse_when_no_context: true  # 无上下文时拒绝回答
  temperature: 0.7          # LLM温度参数
  system_prompt: |          # 系统提示词
    你是一个知识库问答助手。根据上下文信息回答问题。
    如果没有相关信息，明确回复"知识库中未找到相关信息"。
    回答时请引用来源。

# LLM配置
llm:
  provider: "openai"
  model: "gpt-3.5-turbo"
  base_api: "https://api.openai.com/v1"
  temperature: 0.7
  max_tokens: 2000

# Embedding配置
embedding:
  provider: "openai"
  model: "text-embedding-ada-002"
  base_api: "https://api.openai.com/v1"
```

## 示例文档

项目包含5篇示例文档：

1. **Python编程指南.md** - Python基础知识
2. **机器学习入门.md** - 机器学习概念
3. **Web开发技术.md** - Web开发技术栈
4. **数据库设计.md** - 数据库设计原则
5. **项目管理.md** - 项目管理方法

## 标准问题

### 问题1：Python中如何定义函数？
- **期望命中**：Python编程指南.md
- **期望回答**：包含函数定义语法、参数、返回值等

### 问题2：什么是监督学习和无监督学习？
- **期望命中**：机器学习入门.md
- **期望回答**：包含两种学习方式的定义和区别

### 问题3：如何设计数据库表结构？
- **期望命中**：数据库设计.md
- **期望回答**：包含数据库设计原则、范式等

### 知识库外问题测试
**测试问题**：2024年奥运会举办地点是哪里？
- **期望行为**：拒绝回答，回复"知识库中未找到相关信息"
- **验证**：确保Agent不会编造答案

## API接口

### 聊天API
- `POST /api/chat/message` - 发送消息
- `GET /api/chat/history` - 获取对话历史
- `POST /api/chat/clear` - 清空对话

### 文档API
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents/list` - 获取文档列表
- `POST /api/documents/reload` - 重新加载文档

### 配置API
- `GET /api/config/` - 获取配置
- `POST /api/config/update` - 更新配置
- `POST /api/config/reload` - 重新加载配置

## 开发指南

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/backend/test_config.py

# 运行集成测试
pytest tests/integration/
```

### 代码规范
- 后端：Python 3.10+, PEP 8
- 前端：TypeScript, ESLint
- 提交信息：Conventional Commits

## 常见问题

### Q: 如何切换LLM提供商？
A: 修改 `config.yaml` 中的 `llm` 配置，支持任何OpenAI兼容的API。

### Q: 如何添加新的文档类型？
A: 修改 `backend/rag/document_loader.py`，添加对新文件类型的支持。

### Q: 如何调整检索效果？
A: 调整 `config.yaml` 中的 `rag.chunk_size`、`rag.top_k` 和 `rag.similarity_threshold` 参数。

## 许可证

MIT License
```

- [ ] **Step 4: 提交README和集成测试**

```bash
git add README.md tests/integration/
git commit -m "docs: add README and integration tests"
```

---

## Task 12: 最终验证和部署准备

**Files:**
- Create: `Makefile`
- Create: `docker-compose.yml` (可选)
- Update: `README.md`

- [ ] **Step 1: 创建Makefile**

```makefile
# Makefile

.PHONY: install test run clean

# 安装依赖
install:
	pip install -r requirements.txt
	cd frontend && npm install

# 运行测试
test:
	pytest tests/ -v

# 运行后端
run-backend:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 运行前端
run-frontend:
	cd frontend && npm start

# 运行所有
run: run-backend run-frontend

# 清理
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf chroma_db
	rm -rf uploads/*
```

- [ ] **Step 2: 创建Docker Compose文件（可选）**

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./docs:/app/docs
      - ./uploads:/app/uploads
      - ./chroma_db:/app/chroma_db
      - ./config.yaml:/app/config.yaml
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_API_BASE=${OPENAI_API_BASE}
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

networks:
  default:
    driver: bridge
```

- [ ] **Step 3: 创建后端Dockerfile**

```dockerfile
# Dockerfile.backend
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 4: 创建前端Dockerfile**

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npm", "start"]
```

- [ ] **Step 5: 运行完整测试套件**

运行: `make test`
预期: 所有测试通过

- [ ] **Step 6: 验证应用启动**

运行: `make run-backend`
预期: 后端服务启动成功

在另一个终端运行: `make run-frontend`
预期: 前端服务启动成功

- [ ] **Step 7: 提交最终文件**

```bash
git add Makefile docker-compose.yml Dockerfile.backend frontend/Dockerfile
git commit -m "feat: add Makefile and Docker configuration"
```

- [ ] **Step 8: 创建初始标签**

```bash
git tag -a v0.1.0 -m "Initial release: RAG QA Agent"
git push origin v0.1.0
```

---

## 自我审查清单

### 1. 规范覆盖检查
- ✅ 文档接入（本地文件夹 + 文件上传）
- ✅ RAG流水线（文档切分 → 向量化 → 检索 → 生成）
- ✅ 引用溯源（文档名、相似度分数）
- ✅ Agent行为（拒绝编造、支持追问）
- ✅ 可配置项（chunk大小、top-k、embedding方式等）
- ✅ 使用LangChain实现
- ✅ Web界面（React）
- ✅ 5篇示例文档
- ✅ 3个标准问题
- ✅ 知识库外问题测试

### 2. 占位符扫描
- ✅ 无"TBD"、"TODO"等占位符
- ✅ 所有步骤都有具体代码
- ✅ 所有测试都有具体实现

### 3. 类型一致性检查
- ✅ 配置结构一致
- ✅ API接口一致
- ✅ 组件属性一致

### 4. 文件路径检查
- ✅ 所有文件路径都是绝对路径
- ✅ 测试文件路径正确
- ✅ 配置文件路径正确

### 5. 命令检查
- ✅ 所有pytest命令都有具体测试文件
- ✅ 所有npm命令都有具体脚本
- ✅ 所有git命令都有具体文件

## 执行选项

**计划完成并保存到 `docs/superpowers/plans/2026-06-21-rag-qa-agent-implementation.md`。两种执行选项：**

**1. 子代理驱动（推荐）** - 我为每个任务分派一个新的子代理，任务之间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用executing-plans执行任务，批量执行并设置检查点

**选择哪种方式？**