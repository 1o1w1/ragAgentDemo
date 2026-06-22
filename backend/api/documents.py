import os
import shutil
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from rag.document_loader import DocumentLoader
from rag.text_splitter import TextSplitter
from rag.vector_store import VectorStoreManager
from utils.logger import setup_logger

logger = setup_logger(__name__)

documents_router = APIRouter(prefix="/api/documents", tags=["documents"])

_document_loader: Optional[DocumentLoader] = None
_text_splitter: Optional[TextSplitter] = None
_vector_store_manager: Optional[VectorStoreManager] = None
_upload_dir: str = "./uploads"


def set_document_services(
    document_loader: DocumentLoader,
    text_splitter: TextSplitter,
    vector_store_manager: VectorStoreManager,
    upload_dir: str = "./uploads",
):
    global _document_loader, _text_splitter, _vector_store_manager, _upload_dir
    _document_loader = document_loader
    _text_splitter = text_splitter
    _vector_store_manager = vector_store_manager
    _upload_dir = upload_dir


class DocumentUploadResponse(BaseModel):
    filename: str
    chunks: int
    status: str


class DocumentStatsResponse(BaseModel):
    count: int
    name: str


class DocumentListResponse(BaseModel):
    documents: List[dict]


@documents_router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = Path(file.filename).suffix
    if suffix not in {".md", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Supported: .md, .txt",
        )

    upload_path = Path(_upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / file.filename

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        documents = _document_loader.load_uploaded_file(str(file_path), file.filename)
        if not documents:
            raise HTTPException(status_code=400, detail="Failed to load document")

        chunks = _text_splitter.split_documents(documents)
        _vector_store_manager.add_documents(chunks)

        logger.info(f"Uploaded and indexed {file.filename}: {len(chunks)} chunks")
        return DocumentUploadResponse(
            filename=file.filename,
            chunks=len(chunks),
            status="indexed",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@documents_router.post("/load-directory")
async def load_directory(directory: str = "./docs"):
    path = Path(directory)
    if not path.exists():
        raise HTTPException(status_code=400, detail=f"Directory not found: {directory}")

    try:
        documents = _document_loader.load_directory(directory)
        if not documents:
            return {"status": "no_documents_found", "chunks": 0}

        chunks = _text_splitter.split_documents(documents)
        _vector_store_manager.add_documents(chunks)

        logger.info(f"Loaded directory {directory}: {len(chunks)} chunks from {len(documents)} documents")
        return {
            "status": "indexed",
            "documents": len(documents),
            "chunks": len(chunks),
        }
    except Exception as e:
        logger.error(f"Error loading directory {directory}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@documents_router.get("/stats", response_model=DocumentStatsResponse)
async def get_stats():
    stats = _vector_store_manager.get_collection_stats()
    return DocumentStatsResponse(**stats)


@documents_router.delete("/")
async def delete_all_documents():
    try:
        _vector_store_manager.delete_collection()
        logger.info("Deleted all documents from vector store")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error deleting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@documents_router.get("/uploads")
async def list_uploads():
    upload_path = Path(_upload_dir)
    if not upload_path.exists():
        return {"files": []}

    files = [
        {"name": f.name, "size": f.stat().st_size}
        for f in upload_path.iterdir()
        if f.is_file()
    ]
    return {"files": files}
