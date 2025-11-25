"""Byzantine Fault Tolerant consensus for multi-agent decisions."""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import hashlib

from local_bridge import ollama


class MessageType(Enum):
    PRE_PREPARE = "pre_prepare"
    PREPARE = "prepare"
    COMMIT = "commit"


@dataclass
class BFTMessage:
    msg_type: MessageType
    view: int
    sequence: int
    digest: str
    sender: str
    content: Any = None


class BFTConsensus:
    """PBFT-style consensus for agent agreement."""
    
    def __init__(self, node_id: str, total_nodes: int = 4):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.f = (total_nodes - 1) // 3  # max faulty nodes
        self.view = 0
        self.sequence = 0
        self.log: List[BFTMessage] = []
        self.prepared: Dict[str, int] = {}
        self.committed: Dict[str, int] = {}
    
    def propose(self, task: str) -> str:
        """Propose a task and reach consensus."""
        # Generate response
        response = ollama.generate(task)
        digest = self._hash(response)
        
        # Pre-prepare phase (as leader)
        self._broadcast(BFTMessage(
            msg_type=MessageType.PRE_PREPARE,
            view=self.view,
            sequence=self.sequence,
            digest=digest,
            sender=self.node_id,
            content=response
        ))
        
        # Simulate prepare phase
        self.prepared[digest] = self.prepared.get(digest, 0) + 1
        
        # Check if we have 2f+1 prepares
        if self.prepared.get(digest, 0) >= 2 * self.f + 1:
            self.committed[digest] = self.committed.get(digest, 0) + 1
        
        # Check commit
        if self.committed.get(digest, 0) >= 2 * self.f + 1:
            self.sequence += 1
            return response
        
        return "Consensus not reached"
    
    def _broadcast(self, msg: BFTMessage):
        """Broadcast message to all nodes."""
        self.log.append(msg)
    
    def _hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_state(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "view": self.view,
            "sequence": self.sequence,
            "log_size": len(self.log)
        }
