"""Distributed tracing for agent workflows."""
import time
import uuid
import json
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
import threading


@dataclass
class Span:
    """Single tracing span."""
    name: str
    trace_id: str
    span_id: str
    parent_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    status: str = "running"
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    def end(self, status: str = "ok"):
        """End the span."""
        self.end_time = time.time()
        self.status = status
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Add event to span."""
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {}
        })
    
    def set_attribute(self, key: str, value: Any):
        """Set span attribute."""
        self.attributes[key] = value
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class Tracer:
    """Lightweight tracer for agent workflows."""
    
    def __init__(self, service_name: str = "autogen-local",
                 exporter: Callable[[Span], None] = None):
        self.service_name = service_name
        self._exporter = exporter or self._default_exporter
        self._active_spans: Dict[str, Span] = {}
        self._completed_spans: List[Span] = []
        self._lock = threading.Lock()
        self._current_trace_id: Optional[str] = None
        self._span_stack: List[str] = []
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        return uuid.uuid4().hex[:16]
    
    def _default_exporter(self, span: Span):
        """Default exporter prints to console."""
        duration = span.duration_ms or 0
        print(f"[TRACE] {span.name} - {duration:.2f}ms - {span.status}")
    
    def start_trace(self, name: str = "root") -> str:
        """Start a new trace."""
        self._current_trace_id = self._generate_id()
        span = self.start_span(name)
        return self._current_trace_id
    
    def start_span(self, name: str, attributes: Dict[str, Any] = None) -> Span:
        """Start a new span."""
        trace_id = self._current_trace_id or self._generate_id()
        span_id = self._generate_id()
        parent_id = self._span_stack[-1] if self._span_stack else None
        
        span = Span(
            name=name,
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            attributes=attributes or {}
        )
        
        with self._lock:
            self._active_spans[span_id] = span
            self._span_stack.append(span_id)
        
        return span
    
    def end_span(self, span: Span, status: str = "ok"):
        """End a span."""
        span.end(status)
        
        with self._lock:
            if span.span_id in self._active_spans:
                del self._active_spans[span.span_id]
            if span.span_id in self._span_stack:
                self._span_stack.remove(span.span_id)
            self._completed_spans.append(span)
        
        self._exporter(span)
    
    @contextmanager
    def span(self, name: str, attributes: Dict[str, Any] = None):
        """Context manager for spans."""
        s = self.start_span(name, attributes)
        try:
            yield s
            self.end_span(s, "ok")
        except Exception as e:
            s.set_attribute("error", str(e))
            self.end_span(s, "error")
            raise
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace."""
        with self._lock:
            return [s for s in self._completed_spans if s.trace_id == trace_id]
    
    def export_trace(self, trace_id: str) -> str:
        """Export trace as JSON."""
        spans = self.get_trace(trace_id)
        return json.dumps([s.to_dict() for s in spans], indent=2)
    
    def clear(self):
        """Clear all spans."""
        with self._lock:
            self._active_spans.clear()
            self._completed_spans.clear()
            self._span_stack.clear()
            self._current_trace_id = None
