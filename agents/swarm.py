"""Swarm intelligence for distributed agent coordination."""
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from local_bridge import ollama, Message


@dataclass
class SwarmAgent:
    """Individual agent in a swarm."""
    id: str
    position: Dict[str, float] = field(default_factory=dict)
    velocity: Dict[str, float] = field(default_factory=dict)
    best_position: Dict[str, float] = field(default_factory=dict)
    best_score: float = float('-inf')
    
    def evaluate(self, task: str, context: str) -> tuple[str, float]:
        """Evaluate task and return response with confidence score."""
        prompt = f"Context: {context}\n\nTask: {task}\n\nProvide your solution and rate confidence 0-100."
        response = ollama.generate(prompt)
        # Extract confidence from response (simplified)
        confidence = self._extract_confidence(response)
        return response, confidence
    
    def _extract_confidence(self, response: str) -> float:
        """Extract confidence score from response."""
        import re
        match = re.search(r'(\d+)%|confidence[:\s]*(\d+)', response.lower())
        if match:
            return float(match.group(1) or match.group(2))
        return 50.0  # default


class Swarm:
    """Swarm of agents using particle swarm optimization."""
    
    def __init__(self, size: int = 5, inertia: float = 0.7):
        self.agents = [SwarmAgent(id=f"agent_{i}") for i in range(size)]
        self.global_best: Dict[str, Any] = {}
        self.global_best_score = float('-inf')
        self.inertia = inertia
    
    def solve(self, task: str, iterations: int = 3) -> str:
        """Solve task using swarm intelligence."""
        context = ""
        
        for iteration in range(iterations):
            responses = []
            
            # Parallel evaluation
            with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
                futures = {
                    executor.submit(agent.evaluate, task, context): agent
                    for agent in self.agents
                }
                for future in as_completed(futures):
                    agent = futures[future]
                    response, score = future.result()
                    responses.append((agent, response, score))
                    
                    if score > agent.best_score:
                        agent.best_score = score
                        agent.best_position = {"response": response}
                    
                    if score > self.global_best_score:
                        self.global_best_score = score
                        self.global_best = {"response": response, "agent": agent.id}
            
            # Update context with best responses for next iteration
            best_responses = sorted(responses, key=lambda x: x[2], reverse=True)[:2]
            context = "\n".join([f"Previous solution (score {r[2]}): {r[1][:200]}" for r in best_responses])
        
        return self.global_best.get("response", "No solution found")
    
    def get_consensus(self) -> str:
        """Get consensus from all agents on current best."""
        return self.global_best.get("response", "")
