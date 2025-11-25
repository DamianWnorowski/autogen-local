"""Global configuration for AutoGen Local."""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class OllamaConfig:
    """Ollama server configuration."""
    base_url: str = "http://localhost:11434"
    default_model: str = os.getenv("DEFAULT_MODEL", "llama3:8b")
    code_model: str = os.getenv("CODE_MODEL", "deepseek-coder:13b")
    embedding_model: str = "nomic-embed-text"
    timeout: int = 120
    max_retries: int = 3


@dataclass
class AgentConfig:
    """Base agent configuration."""
    max_iterations: int = 10
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = ""
    tools: list = field(default_factory=list)


@dataclass
class MemoryConfig:
    """Memory and persistence settings."""
    db_path: Path = Path("./data/memory.db")
    embedding_dim: int = 768
    max_context_items: int = 50
    similarity_threshold: float = 0.7


@dataclass
class CommsConfig:
    """Communication layer settings."""
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    zmq_pub_port: int = 5555
    zmq_sub_port: int = 5556
    message_ttl: int = 3600


@dataclass
class Config:
    """Main configuration container."""
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    comms: CommsConfig = field(default_factory=CommsConfig)
    
    # paths
    data_dir: Path = Path("./data")
    log_dir: Path = Path("./logs")
    
    # feature flags
    enable_tracing: bool = True
    enable_persistence: bool = True
    enable_distributed: bool = False
    
    def __post_init__(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)


# global config instance
config = Config()
