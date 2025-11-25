"""Redis-based pub/sub message bus for agent communication."""
import json
import threading
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
import time

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class Message:
    """Message structure for bus communication."""
    topic: str
    payload: Any
    sender: str
    timestamp: float
    msg_id: str = ""


class RedisBus:
    """Redis pub/sub message bus for distributed agent communication."""
    
    def __init__(self, host: str = "localhost", port: int = 6379,
                 db: int = 0, prefix: str = "autogen"):
        if not REDIS_AVAILABLE:
            raise ImportError("redis package required: pip install redis")
        
        self.host = host
        self.port = port
        self.prefix = prefix
        self._client = redis.Redis(host=host, port=port, db=db)
        self._pubsub = self._client.pubsub()
        self._subscribers: Dict[str, List[Callable]] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._msg_counter = 0
    
    def _make_channel(self, topic: str) -> str:
        """Create prefixed channel name."""
        return f"{self.prefix}:{topic}"
    
    def _generate_id(self) -> str:
        """Generate unique message ID."""
        self._msg_counter += 1
        return f"{time.time():.6f}-{self._msg_counter}"
    
    def publish(self, topic: str, payload: Any, sender: str = "unknown") -> bool:
        """Publish message to topic."""
        try:
            msg = Message(
                topic=topic,
                payload=payload,
                sender=sender,
                timestamp=time.time(),
                msg_id=self._generate_id()
            )
            channel = self._make_channel(topic)
            data = json.dumps({
                "topic": msg.topic,
                "payload": msg.payload,
                "sender": msg.sender,
                "timestamp": msg.timestamp,
                "msg_id": msg.msg_id
            })
            self._client.publish(channel, data)
            return True
        except Exception as e:
            print(f"Publish error: {e}")
            return False
    
    def subscribe(self, topic: str, callback: Callable[[Message], None]) -> None:
        """Subscribe to topic with callback."""
        channel = self._make_channel(topic)
        
        if topic not in self._subscribers:
            self._subscribers[topic] = []
            self._pubsub.subscribe(channel)
        
        self._subscribers[topic].append(callback)
    
    def unsubscribe(self, topic: str, callback: Callable = None) -> None:
        """Unsubscribe from topic."""
        if topic in self._subscribers:
            if callback:
                self._subscribers[topic] = [
                    c for c in self._subscribers[topic] if c != callback
                ]
            else:
                del self._subscribers[topic]
                self._pubsub.unsubscribe(self._make_channel(topic))
    
    def _listener_loop(self):
        """Background thread for message handling."""
        for message in self._pubsub.listen():
            if not self._running:
                break
            
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    msg = Message(**data)
                    
                    if msg.topic in self._subscribers:
                        for callback in self._subscribers[msg.topic]:
                            try:
                                callback(msg)
                            except Exception as e:
                                print(f"Callback error: {e}")
                except Exception as e:
                    print(f"Message parse error: {e}")
    
    def start(self) -> None:
        """Start listening for messages."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._listener_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop listening."""
        self._running = False
        if self._thread:
            self._pubsub.unsubscribe()
            self._thread.join(timeout=1.0)
            self._thread = None
    
    def request(self, topic: str, payload: Any, sender: str,
                timeout: float = 5.0) -> Optional[Any]:
        """Synchronous request-response pattern."""
        response_topic = f"{topic}:response:{self._generate_id()}"
        response = {"received": False, "data": None}
        
        def handler(msg: Message):
            response["received"] = True
            response["data"] = msg.payload
        
        self.subscribe(response_topic, handler)
        
        self.publish(topic, {
            "payload": payload,
            "response_topic": response_topic
        }, sender)
        
        start = time.time()
        while not response["received"] and time.time() - start < timeout:
            time.sleep(0.01)
        
        self.unsubscribe(response_topic)
        return response["data"] if response["received"] else None
    
    def close(self) -> None:
        """Clean up connections."""
        self.stop()
        self._pubsub.close()
        self._client.close()
