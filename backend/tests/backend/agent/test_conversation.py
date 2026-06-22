import pytest
from unittest.mock import patch
from agent.conversation import ConversationManager, Message


def test_add_user_message():
    manager = ConversationManager(max_history=5)
    msg = manager.add_user_message("你好")

    assert msg.role == "user"
    assert msg.content == "你好"
    assert len(manager.messages) == 1


def test_add_assistant_message():
    manager = ConversationManager(max_history=5)
    msg = manager.add_assistant_message("你好！有什么可以帮助你的吗？")

    assert msg.role == "assistant"
    assert msg.content == "你好！有什么可以帮助你的吗？"
    assert len(manager.messages) == 1


def test_get_history():
    manager = ConversationManager(max_history=5)
    manager.add_user_message("问题")
    manager.add_assistant_message("回答")

    history = manager.get_history()

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "问题"
    assert "timestamp" in history[0]
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "回答"


def test_get_messages_for_llm():
    manager = ConversationManager(max_history=5)
    manager.add_user_message("问题")
    manager.add_assistant_message("回答")

    messages = manager.get_messages_for_llm()

    assert len(messages) == 2
    assert messages[0] == {"role": "user", "content": "问题"}
    assert messages[1] == {"role": "assistant", "content": "回答"}


def test_get_last_user_message():
    manager = ConversationManager(max_history=5)
    manager.add_user_message("第一个问题")
    manager.add_assistant_message("第一个回答")
    manager.add_user_message("第二个问题")

    assert manager.get_last_user_message() == "第二个问题"


def test_get_last_user_message_empty():
    manager = ConversationManager(max_history=5)
    assert manager.get_last_user_message() is None


def test_trim_history():
    manager = ConversationManager(max_history=2)

    for i in range(5):
        manager.add_user_message(f"问题{i}")
        manager.add_assistant_message(f"回答{i}")

    assert len(manager.messages) == 4


def test_clear():
    manager = ConversationManager(max_history=5)
    manager.add_user_message("问题")
    manager.add_assistant_message("回答")

    manager.clear()

    assert len(manager.messages) == 0
    assert manager.get_last_user_message() is None


def test_update_config():
    manager = ConversationManager(max_history=5)
    manager.update_config(max_history=3)

    assert manager.max_history == 3


def test_message_to_dict():
    msg = Message(role="user", content="测试", metadata={"key": "value"})
    d = msg.to_dict()

    assert d["role"] == "user"
    assert d["content"] == "测试"
    assert d["metadata"] == {"key": "value"}
    assert "timestamp" in d


def test_conversation_id_format():
    manager = ConversationManager(max_history=5)
    assert len(manager.conversation_id) == 15
    assert "_" in manager.conversation_id
