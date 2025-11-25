"""State management for multi-agent workflows."""
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import copy
import time


class StateScope(Enum):
    """Scope levels for state."""
    GLOBAL = "global"
    WORKFLOW = "workflow"
    AGENT = "agent"
    TASK = "task"


@dataclass
class StateChange:
    """Record of state change."""
    key: str
    old_value: Any
    new_value: Any
    scope: StateScope
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"


class StateManager:
    """Thread-safe state management with scoping and history."""
    
    def __init__(self, enable_history: bool = True, max_history: int = 100):
        self._state: Dict[StateScope, Dict[str, Any]] = {
            scope: {} for scope in StateScope
        }
        self._lock = threading.RLock()
        self._history: List[StateChange] = []
        self._enable_history = enable_history
        self._max_history = max_history
        self._watchers: Dict[str, List[Callable]] = {}
    
    def set(self, key: str, value: Any, scope: StateScope = StateScope.WORKFLOW,
            source: str = "unknown") -> None:
        """Set state value with optional change tracking."""
        with self._lock:
            old_value = self._state[scope].get(key)
            self._state[scope][key] = copy.deepcopy(value)
            
            if self._enable_history:
                change = StateChange(
                    key=key,
                    old_value=old_value,
                    new_value=value,
                    scope=scope,
                    source=source
                )
                self._history.append(change)
                if len(self._history) > self._max_history:
                    self._history.pop(0)
            
            self._notify_watchers(key, old_value, value, scope)
    
    def get(self, key: str, scope: StateScope = StateScope.WORKFLOW,
            default: Any = None) -> Any:
        """Get state value."""
        with self._lock:
            value = self._state[scope].get(key, default)
            return copy.deepcopy(value) if value is not None else default
    
    def delete(self, key: str, scope: StateScope = StateScope.WORKFLOW) -> bool:
        """Remove state value."""
        with self._lock:
            if key in self._state[scope]:
                del self._state[scope][key]
                return True
            return False
    
    def get_all(self, scope: StateScope = StateScope.WORKFLOW) -> Dict[str, Any]:
        """Get all state for a scope."""
        with self._lock:
            return copy.deepcopy(self._state[scope])
    
    def merge(self, data: Dict[str, Any], scope: StateScope = StateScope.WORKFLOW,
              source: str = "unknown") -> None:
        """Merge dictionary into state."""
        for key, value in data.items():
            self.set(key, value, scope, source)
    
    def watch(self, key: str, callback: Callable[[Any, Any], None]) -> None:
        """Register callback for state changes."""
        if key not in self._watchers:
            self._watchers[key] = []
        self._watchers[key].append(callback)
    
    def unwatch(self, key: str, callback: Callable = None) -> None:
        """Remove watcher(s) for key."""
        if key in self._watchers:
            if callback:
                self._watchers[key] = [c for c in self._watchers[key] if c != callback]
            else:
                del self._watchers[key]
    
    def _notify_watchers(self, key: str, old_value: Any, new_value: Any,
                         scope: StateScope) -> None:
        """Notify registered watchers of change."""
        if key in self._watchers:
            for callback in self._watchers[key]:
                try:
                    callback(old_value, new_value)
                except Exception as e:
                    print(f"Watcher error for {key}: {e}")
    
    def get_history(self, key: str = None, scope: StateScope = None,
                    limit: int = None) -> List[StateChange]:
        """Get state change history with optional filters."""
        with self._lock:
            history = self._history.copy()
            
            if key:
                history = [h for h in history if h.key == key]
            if scope:
                history = [h for h in history if h.scope == scope]
            if limit:
                history = history[-limit:]
            
            return history
    
    def rollback(self, steps: int = 1) -> bool:
        """Rollback state changes."""
        with self._lock:
            if steps > len(self._history):
                return False
            
            for _ in range(steps):
                change = self._history.pop()
                if change.old_value is None:
                    self._state[change.scope].pop(change.key, None)
                else:
                    self._state[change.scope][change.key] = change.old_value
            
            return True
    
    def clear(self, scope: StateScope = None) -> None:
        """Clear state for scope or all scopes."""
        with self._lock:
            if scope:
                self._state[scope] = {}
            else:
                for s in StateScope:
                    self._state[s] = {}
            self._history = []
    
    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Create full state snapshot."""
        with self._lock:
            return {
                scope.value: copy.deepcopy(data)
                for scope, data in self._state.items()
            }
    
    def restore(self, snapshot: Dict[str, Dict[str, Any]]) -> None:
        """Restore state from snapshot."""
        with self._lock:
            for scope_name, data in snapshot.items():
                scope = StateScope(scope_name)
                self._state[scope] = copy.deepcopy(data)
