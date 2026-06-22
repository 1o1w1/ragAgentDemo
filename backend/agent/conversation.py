from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Message:
    def __init__(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class ConversationManager:
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.messages: List[Message] = []
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        message = Message(role="user", content=content, metadata=metadata)
        self.messages.append(message)
        self._trim_history()
        logger.info(f"Added user message to conversation {self.conversation_id}")
        return message

    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        message = Message(role="assistant", content=content, metadata=metadata)
        self.messages.append(message)
        self._trim_history()
        logger.info(f"Added assistant message to conversation {self.conversation_id}")
        return message

    def get_history(self) -> List[Dict[str, Any]]:
        return [msg.to_dict() for msg in self.messages]

    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def get_last_user_message(self) -> Optional[str]:
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None

    def clear(self):
        self.messages.clear()
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info("Conversation cleared")

    def _trim_history(self):
        if len(self.messages) > self.max_history * 2:
            self.messages = self.messages[-(self.max_history * 2):]
            logger.info(f"Trimmed conversation history to {self.max_history * 2} messages")

    def update_config(self, max_history: int = None):
        if max_history is not None:
            self.max_history = max_history
            self._trim_history()
