import pytest
import tempfile
import yaml
from pathlib import Path
from config import ConfigManager, AppConfig


def test_default_config():
    config = AppConfig()
    assert config.rag.chunk_size == 512
    assert config.rag.top_k == 5
    assert config.agent.refuse_when_no_context is True


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
