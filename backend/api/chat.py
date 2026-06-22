from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
import json

chat_router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query")


class ChatResponse(BaseModel):
    answer: str
    reasoning: Optional[str] = None
    citations: List[Dict[str, Any]]
    has_context: bool


class ConversationHistoryResponse(BaseModel):
    history: List[Dict[str, Any]]


_agent_behavior = None


def set_agent_behavior(agent):
    global _agent_behavior
    _agent_behavior = agent


def get_agent_behavior():
    if _agent_behavior is None:
        raise RuntimeError("AgentBehavior not initialized")
    return _agent_behavior


@chat_router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    agent = get_agent_behavior()
    try:
        result = await agent.chat(request.query)
        return ChatResponse(
            answer=result["answer"],
            reasoning=result.get("reasoning"),
            citations=result["citations"],
            has_context=result["has_context"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/stream")
async def chat_stream_post(request: ChatRequest):
    agent = get_agent_behavior()

    async def event_generator():
        try:
            async for event in agent.chat_stream(request.query):
                if event["type"] == "token":
                    yield {
                        "event": "token",
                        "data": json.dumps({"content": event["content"]})
                    }
                elif event["type"] == "reasoning":
                    yield {
                        "event": "reasoning",
                        "data": json.dumps({"content": event["content"]})
                    }
                elif event["type"] == "citations":
                    yield {
                        "event": "citations",
                        "data": json.dumps({
                            "citations": event["citations"],
                            "has_context": event["has_context"],
                        })
                    }

            yield {
                "event": "done",
                "data": json.dumps({"status": "complete"})
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }

    return EventSourceResponse(event_generator())


@chat_router.get("/stream")
async def chat_stream_get(query: str):
    agent = get_agent_behavior()

    async def event_generator():
        try:
            async for event in agent.chat_stream(query):
                if event["type"] == "token":
                    yield {
                        "event": "token",
                        "data": json.dumps({"content": event["content"]})
                    }
                elif event["type"] == "reasoning":
                    yield {
                        "event": "reasoning",
                        "data": json.dumps({"content": event["content"]})
                    }
                elif event["type"] == "citations":
                    yield {
                        "event": "citations",
                        "data": json.dumps({
                            "citations": event["citations"],
                            "has_context": event["has_context"],
                        })
                    }

            yield {
                "event": "done",
                "data": json.dumps({"status": "complete"})
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }

    return EventSourceResponse(event_generator())


@chat_router.get("/history", response_model=ConversationHistoryResponse)
async def get_history():
    agent = get_agent_behavior()
    history = agent.get_conversation_history()
    return ConversationHistoryResponse(history=history)


@chat_router.delete("/history")
async def clear_history():
    agent = get_agent_behavior()
    agent.clear_conversation()
    return {"status": "ok"}
