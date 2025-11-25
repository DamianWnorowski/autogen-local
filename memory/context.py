"""Context window management for conversations."""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time


@dataclass
class Message:
    """Single message in context."""
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0


class ContextWindow:
    """Manages conversation context with token limits."""
    
    def __init__(self, max_tokens: int = 4096, reserve_tokens: int = 512):
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens
        self.available_tokens = max_tokens - reserve_tokens
        self.messages: List[Message] = []
        self.system_message: Optional[Message] = None
        self._total_tokens = 0
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token)."""
        return len(text) // 4 + 1
    
    def set_system_message(self, content: str):
        """Set system message (always kept in context)."""
        tokens = self._estimate_tokens(content)
        self.system_message = Message(
            role="system",
            content=content,
            token_count=tokens
        )
        self.available_tokens = self.max_tokens - self.reserve_tokens - tokens
    
    def add_message(self, role: str, content: str, 
                    metadata: Dict[str, Any] = None) -> bool:
        """Add message to context, returns False if truncation needed."""
        tokens = self._estimate_tokens(content)
        
        while self._total_tokens + tokens > self.available_tokens:
            if not self._evict_oldest():
                return False
        
        msg = Message(
            role=role,
            content=content,
            metadata=metadata or {},
            token_count=tokens
        )
        self.messages.append(msg)
        self._total_tokens += tokens
        return True
    
    def _evict_oldest(self) -> bool:
        """Remove oldest non-system message."""
        if not self.messages:
            return False
        
        removed = self.messages.pop(0)
        self._total_tokens -= removed.token_count
        return True
    
    def get_context(self) -> List[Dict[str, str]]:
        """Get formatted context for LLM."""
        context = []
        
        if self.system_message:
            context.append({
                "role": self.system_message.role,
                "content": self.system_message.content
            })
        
        for msg in self.messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return context
    
    def get_last_n(self, n: int) -> List[Message]:
        """Get last n messages."""
        return self.messages[-n:] if n < len(self.messages) else self.messages.copy()
    
    def search(self, query: str) -> List[Message]:
        """Simple search through message contents."""
        query_lower = query.lower()
        return [m for m in self.messages if query_lower in m.content.lower()]
    
    def clear(self, keep_system: bool = True):
        """Clear context, optionally keeping system message."""
        self.messages = []
        self._total_tokens = 0
        if not keep_system:
            self.system_message = None
            self.available_tokens = self.max_tokens - self.reserve_tokens
    
    def summarize_old(self, summarizer_fn, keep_recent: int = 5) -> str:
        """Summarize older messages using provided function."""
        if len(self.messages) <= keep_recent:
            return ""
        
        old_messages = self.messages[:-keep_recent]
        old_content = "\n".join([f"{m.role}: {m.content}" for m in old_messages])
        
        summary = summarizer_fn(old_content)
        
        self.messages = self.messages[-keep_recent:]
        self._total_tokens = sum(m.token_count for m in self.messages)
        
        self.add_message("system", f"[Previous conversation summary: {summary}]")
        
        return summary
    
    @property
    def token_usage(self) -> Dict[str, int]:
        """Get current token usage stats."""
        system_tokens = self.system_message.token_count if self.system_message else 0
        return {
            "total": self._total_tokens + system_tokens,
            "messages": self._total_tokens,
            "system": system_tokens,
            "available": self.available_tokens - self._total_tokens,
            "max": self.max_tokens
        }
    
    def __len__(self) -> int:
        return len(self.messages)
