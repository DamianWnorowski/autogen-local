"""ZeroMQ mesh network for peer-to-peer agent communication."""
import json
import threading
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass
import time

try:
    import zmq
    ZMQ_AVAILABLE = True
except ImportError:
    ZMQ_AVAILABLE = False


@dataclass
class Peer:
    """Peer node in the mesh."""
    node_id: str
    address: str
    last_seen: float
    metadata: Dict[str, Any] = None


class ZMQMesh:
    """ZeroMQ-based mesh network for direct agent communication."""
    
    def __init__(self, node_id: str, bind_address: str = "tcp://*:5555"):
        if not ZMQ_AVAILABLE:
            raise ImportError("pyzmq package required: pip install pyzmq")
        
        self.node_id = node_id
        self.bind_address = bind_address
        self._context = zmq.Context()
        
        self._router = self._context.socket(zmq.ROUTER)
        self._router.bind(bind_address)
        
        self._peers: Dict[str, Peer] = {}
        self._peer_sockets: Dict[str, zmq.Socket] = {}
        self._handlers: Dict[str, Callable] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def connect_peer(self, node_id: str, address: str,
                     metadata: Dict[str, Any] = None) -> bool:
        """Connect to a peer node."""
        try:
            socket = self._context.socket(zmq.DEALER)
            socket.setsockopt_string(zmq.IDENTITY, self.node_id)
            socket.connect(address)
            
            self._peer_sockets[node_id] = socket
            self._peers[node_id] = Peer(
                node_id=node_id,
                address=address,
                last_seen=time.time(),
                metadata=metadata or {}
            )
            return True
        except Exception as e:
            print(f"Connect error: {e}")
            return False
    
    def disconnect_peer(self, node_id: str) -> bool:
        """Disconnect from peer."""
        if node_id in self._peer_sockets:
            self._peer_sockets[node_id].close()
            del self._peer_sockets[node_id]
        if node_id in self._peers:
            del self._peers[node_id]
        return True
    
    def send(self, target_id: str, msg_type: str, payload: Any) -> bool:
        """Send message to specific peer."""
        if target_id not in self._peer_sockets:
            return False
        
        try:
            message = json.dumps({
                "from": self.node_id,
                "type": msg_type,
                "payload": payload,
                "timestamp": time.time()
            })
            self._peer_sockets[target_id].send_string(message)
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def broadcast(self, msg_type: str, payload: Any,
                  exclude: Set[str] = None) -> int:
        """Broadcast message to all peers."""
        exclude = exclude or set()
        sent = 0
        for peer_id in self._peers:
            if peer_id not in exclude:
                if self.send(peer_id, msg_type, payload):
                    sent += 1
        return sent
    
    def register_handler(self, msg_type: str,
                        handler: Callable[[str, Any], None]) -> None:
        """Register handler for message type."""
        self._handlers[msg_type] = handler
    
    def _receiver_loop(self):
        """Background thread for receiving messages."""
        poller = zmq.Poller()
        poller.register(self._router, zmq.POLLIN)
        
        while self._running:
            try:
                socks = dict(poller.poll(100))
                
                if self._router in socks:
                    identity, _, msg_bytes = self._router.recv_multipart()
                    data = json.loads(msg_bytes.decode())
                    
                    sender = data.get("from", "unknown")
                    msg_type = data.get("type", "")
                    payload = data.get("payload")
                    
                    if sender in self._peers:
                        self._peers[sender].last_seen = time.time()
                    
                    if msg_type in self._handlers:
                        try:
                            self._handlers[msg_type](sender, payload)
                        except Exception as e:
                            print(f"Handler error: {e}")
            except zmq.ZMQError:
                continue
            except Exception as e:
                print(f"Receive error: {e}")
    
    def start(self) -> None:
        """Start receiving messages."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._receiver_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop receiving."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
    
    def get_peers(self) -> List[Peer]:
        """Get list of connected peers."""
        return list(self._peers.values())
    
    def close(self) -> None:
        """Clean up all connections."""
        self.stop()
        for socket in self._peer_sockets.values():
            socket.close()
        self._router.close()
        self._context.term()
