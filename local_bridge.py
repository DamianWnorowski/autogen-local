"""Local LLM bridge using Ollama."""
import json
import httpx
from typing import Optional, List, Dict, Any, Generator
from dataclasses import dataclass
from config import config


@dataclass
class Message:
    """Chat message."""
    role: str
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class OllamaClient:
    """Wrapper for Ollama API."""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config.ollama.base_url
        self.client = httpx.Client(timeout=config.ollama.timeout)
    
    def generate(self, prompt: str, model: Optional[str] = None, 
                 stream: bool = False, **kwargs) -> str:
        """Generate completion from prompt."""
        model = model or config.ollama.default_model
        
        response = self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": stream,
                **kwargs
            }
        )
        response.raise_for_status()
        return response.json()["response"]
    
    def chat(self, messages: List[Message], model: Optional[str] = None,
             stream: bool = False, **kwargs) -> str:
        """Chat completion with message history."""
        model = model or config.ollama.default_model
        
        response = self.client.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": [m.to_dict() for m in messages],
                "stream": stream,
                **kwargs
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    
    def embed(self, text: str, model: Optional[str] = None) -> List[float]:
        """Get embeddings for text."""
        model = model or config.ollama.embedding_model
        
        response = self.client.post(
            f"{self.base_url}/api/embeddings",
            json={"model": model, "prompt": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]
    
    def list_models(self) -> List[str]:
        """List available models."""
        response = self.client.get(f"{self.base_url}/api/tags")
        response.raise_for_status()
        return [m["name"] for m in response.json()["models"]]
    
    def is_healthy(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False


# global client instance
ollama = OllamaClient()
