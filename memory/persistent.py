"""Persistent disk-based memory storage."""
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class MemoryEntry:
    """Single memory entry with metadata."""
    key: str
    value: Any
    created_at: float
    ttl: Optional[float] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)


class PersistentMemory:
    """Disk-backed memory with JSON serialization."""
    
    def __init__(self, storage_dir: str = ".memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._index: Dict[str, str] = {}
        self._load_index()
    
    def _load_index(self):
        """Load memory index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self._index = json.load(f)
            except json.JSONDecodeError:
                self._index = {}
    
    def _save_index(self):
        """Persist index to disk."""
        with open(self.index_file, 'w') as f:
            json.dump(self._index, f, indent=2)
    
    def _get_entry_path(self, key: str) -> Path:
        """Get file path for a memory entry."""
        safe_key = key.replace('/', '_').replace('\\', '_')
        return self.storage_dir / f"{safe_key}.json"
    
    def store(self, key: str, value: Any, ttl: Optional[float] = None,
              tags: List[str] = None) -> bool:
        """Store value with optional TTL and tags."""
        entry = MemoryEntry(
            key=key,
            value=value,
            created_at=time.time(),
            ttl=ttl,
            tags=tags or []
        )
        
        entry_path = self._get_entry_path(key)
        try:
            with open(entry_path, 'w') as f:
                json.dump(asdict(entry), f, indent=2, default=str)
            self._index[key] = str(entry_path)
            self._save_index()
            return True
        except Exception as e:
            print(f"Failed to store {key}: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value by key, returns None if expired or missing."""
        if key not in self._index:
            return None
        
        entry_path = Path(self._index[key])
        if not entry_path.exists():
            del self._index[key]
            self._save_index()
            return None
        
        try:
            with open(entry_path, 'r') as f:
                data = json.load(f)
            entry = MemoryEntry(**data)
            
            if entry.is_expired():
                self.delete(key)
                return None
            
            return entry.value
        except Exception:
            return None
    
    def delete(self, key: str) -> bool:
        """Remove entry from memory."""
        if key not in self._index:
            return False
        
        entry_path = Path(self._index[key])
        if entry_path.exists():
            entry_path.unlink()
        
        del self._index[key]
        self._save_index()
        return True
    
    def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Find all entries with given tag."""
        results = []
        for key in list(self._index.keys()):
            entry_path = Path(self._index[key])
            if entry_path.exists():
                with open(entry_path, 'r') as f:
                    data = json.load(f)
                if tag in data.get('tags', []):
                    entry = MemoryEntry(**data)
                    if not entry.is_expired():
                        results.append({'key': key, 'value': entry.value})
        return results
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries, returns count removed."""
        removed = 0
        for key in list(self._index.keys()):
            entry_path = Path(self._index[key])
            if entry_path.exists():
                with open(entry_path, 'r') as f:
                    data = json.load(f)
                entry = MemoryEntry(**data)
                if entry.is_expired():
                    self.delete(key)
                    removed += 1
        return removed
    
    def list_keys(self) -> List[str]:
        """Get all stored keys."""
        return list(self._index.keys())
    
    def clear(self):
        """Remove all stored memories."""
        for key in list(self._index.keys()):
            self.delete(key)
        self._index = {}
        self._save_index()
