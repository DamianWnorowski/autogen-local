"""Tests for config module."""
import pytest
import os
from unittest.mock import patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config, DEFAULT_MODEL, CODE_MODEL, OLLAMA_HOST


class TestConfig:
    """Test configuration loading and defaults."""
    
    def test_default_model_exists(self):
        """Default model should be set."""
        assert DEFAULT_MODEL is not None
        assert isinstance(DEFAULT_MODEL, str)
        assert len(DEFAULT_MODEL) > 0
    
    def test_code_model_exists(self):
        """Code model should be set."""
        assert CODE_MODEL is not None
        assert isinstance(CODE_MODEL, str)
    
    def test_ollama_host_default(self):
        """Ollama host should default to localhost."""
        assert "localhost" in OLLAMA_HOST or "127.0.0.1" in OLLAMA_HOST
    
    @patch.dict(os.environ, {"DEFAULT_MODEL": "custom-model"})
    def test_env_override_model(self):
        """Environment variables should override defaults."""
        # Re-import to pick up env var
        import importlib
        import config
        importlib.reload(config)
        # Note: actual behavior depends on config implementation
    
    def test_config_class_instantiation(self):
        """Config class should instantiate without errors."""
        cfg = Config()
        assert cfg is not None
    
    def test_config_has_required_attributes(self):
        """Config should have required attributes."""
        cfg = Config()
        assert hasattr(cfg, 'model') or hasattr(cfg, 'default_model')


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_invalid_model_handling(self):
        """Should handle invalid model names gracefully."""
        # This tests error handling for bad model names
        pass  # Implement based on actual config behavior
    
    def test_empty_config(self):
        """Empty config should use defaults."""
        cfg = Config()
        # Should not raise
        assert cfg is not None
