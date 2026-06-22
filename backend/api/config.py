from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import AppConfig, config_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)

config_router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigUpdateRequest(BaseModel):
    updates: Dict[str, Any]


@config_router.get("/", response_model=AppConfig)
async def get_config():
    return config_manager.get_config()


@config_router.put("/")
async def update_config(request: ConfigUpdateRequest):
    try:
        config_manager.update_config(request.updates)
        logger.info("Configuration updated")
        return config_manager.get_config()
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@config_router.post("/reload")
async def reload_config():
    try:
        config_manager.reload_config()
        logger.info("Configuration reloaded")
        return config_manager.get_config()
    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@config_router.get("/rag")
async def get_rag_config():
    config = config_manager.get_config()
    return config.rag


@config_router.get("/agent")
async def get_agent_config():
    config = config_manager.get_config()
    return config.agent


@config_router.get("/llm")
async def get_llm_config():
    config = config_manager.get_config()
    return config.llm
