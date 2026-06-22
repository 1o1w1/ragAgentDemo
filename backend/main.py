import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import config_manager
from rag import (
    DocumentLoader,
    TextSplitter,
    EmbeddingManager,
    VectorStoreManager,
    Retriever,
    Generator,
)
from agent import AgentBehavior
from api.chat import chat_router, set_agent_behavior
from api.documents import documents_router, set_document_services
from api.config import config_router
from utils.logger import setup_logger

logger = setup_logger(__name__)

_is_loading = False
_loading_message = ""


def create_agent(config) -> AgentBehavior:
    # For Ollama, use a dummy API key if not set
    api_key = os.getenv("OPENAI_API_KEY", "ollama")
    
    embedding_manager = EmbeddingManager(
        api_key=api_key,
        base_url=config.embedding.base_api,
        model=config.embedding.model,
    )

    vector_store_manager = VectorStoreManager(
        embedding_manager=embedding_manager,
        persist_directory=config.storage.vector_db,
    )

    retriever = Retriever(
        vector_store_manager=vector_store_manager,
        top_k=config.rag.top_k,
        similarity_threshold=config.rag.similarity_threshold,
    )

    generator = Generator(
        api_key=api_key,
        base_url=config.llm.base_api,
        model=config.llm.model,
        temperature=config.agent.temperature,
        max_tokens=config.llm.max_tokens,
        system_prompt=config.agent.system_prompt,
        enable_thinking=config.llm.enable_thinking,
    )

    agent = AgentBehavior(
        retriever=retriever,
        generator=generator,
        max_history=config.agent.max_history,
        refuse_when_no_context=config.agent.refuse_when_no_context,
        show_citation_score=config.ui.show_similarity_score,
    )

    return agent


def create_document_services(config):
    # For Ollama, use a dummy API key if not set
    api_key = os.getenv("OPENAI_API_KEY", "ollama")
    
    document_loader = DocumentLoader()
    text_splitter = TextSplitter(
        chunk_size=config.rag.chunk_size,
        chunk_overlap=config.rag.chunk_overlap,
    )

    embedding_manager = EmbeddingManager(
        api_key=api_key,
        base_url=config.embedding.base_api,
        model=config.embedding.model,
    )

    vector_store_manager = VectorStoreManager(
        embedding_manager=embedding_manager,
        persist_directory=config.storage.vector_db,
    )

    return document_loader, text_splitter, vector_store_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_loading, _loading_message
    logger.info("Starting RAG Knowledge Base API...")
    _is_loading = True
    _loading_message = "Initializing..."
    config = config_manager.get_config()

    agent = create_agent(config)
    set_agent_behavior(agent)

    document_loader, text_splitter, vector_store_manager = create_document_services(config)
    set_document_services(
        document_loader=document_loader,
        text_splitter=text_splitter,
        vector_store_manager=vector_store_manager,
        upload_dir=config.storage.uploads,
    )

    upload_dir = Path(config.storage.uploads)
    upload_dir.mkdir(parents=True, exist_ok=True)

    docs_dir = Path(config.storage.documents)
    if docs_dir.exists():
        logger.info(f"Auto-loading documents from {docs_dir}...")
        _loading_message = "Loading documents..."
        documents = document_loader.load_directory(str(docs_dir))
        if documents:
            vector_store_manager.delete_collection()
            chunks = text_splitter.split_documents(documents)
            logger.info(f"Embedding {len(chunks)} chunks, please wait...")
            _loading_message = f"Embedding {len(chunks)} chunks..."
            vector_store_manager.add_documents(chunks)
            logger.info(f"Auto-loaded {len(chunks)} chunks from {len(documents)} documents")
        else:
            logger.info("No documents found in docs directory")
    else:
        logger.info(f"Documents directory {docs_dir} not found, skipping auto-load")

    _is_loading = False
    _loading_message = ""
    logger.info("RAG Knowledge Base API started successfully")
    yield
    logger.info("Shutting down RAG Knowledge Base API...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG Knowledge Base API",
        description="API for RAG-based knowledge base question answering",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router)
    app.include_router(documents_router)
    app.include_router(config_router)

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "is_loading": _is_loading,
            "loading_message": _loading_message,
        }

    return app


app = create_app()
