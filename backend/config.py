import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class LocalSourceConfig(BaseModel):
    enabled: bool = True
    path: str = "./docs"
    patterns: List[str] = ["**/*.md", "**/*.txt"]


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
    enable_thinking: bool = False


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
        config_data = self.config.model_dump()
        config_data.update(updates)
        self.config = AppConfig(**config_data)
        self._save_config()

    def _save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config.model_dump(), f, default_flow_style=False, allow_unicode=True)


config_manager = ConfigManager()
