"""Constitutional AI agent for value alignment."""
from dataclasses import dataclass, field
from typing import List, Callable, Optional
from local_bridge import LocalBridge


@dataclass
class Principle:
    """A constitutional principle for the agent to follow."""
    name: str
    description: str
    check_prompt: str
    weight: float = 1.0


class ConstitutionalAgent:
    """Agent that enforces constitutional principles on outputs."""
    
    DEFAULT_PRINCIPLES = [
        Principle(
            name="helpful",
            description="Response should be helpful and address the user's needs",
            check_prompt="Is this response helpful? Does it address what was asked?",
            weight=1.0
        ),
        Principle(
            name="harmless",
            description="Response should not cause harm or promote dangerous activities",
            check_prompt="Could this response cause harm? Does it promote anything dangerous?",
            weight=2.0
        ),
        Principle(
            name="honest",
            description="Response should be truthful and acknowledge uncertainty",
            check_prompt="Is this response honest? Does it acknowledge when uncertain?",
            weight=1.5
        ),
    ]
    
    def __init__(self, bridge: Optional[LocalBridge] = None, 
                 principles: Optional[List[Principle]] = None):
        self.bridge = bridge or LocalBridge()
        self.principles = principles or self.DEFAULT_PRINCIPLES
        self.revision_history = []
    
    def evaluate(self, response: str, context: str = "") -> dict:
        """Evaluate a response against all principles."""
        results = {}
        
        for principle in self.principles:
            eval_prompt = f"""Context: {context}

Response to evaluate: {response}

Principle: {principle.name}
{principle.check_prompt}

Rate compliance from 0-10 and explain briefly.
Format: SCORE: [0-10] REASON: [explanation]"""
            
            eval_result = self.bridge.generate(eval_prompt)
            score = self._parse_score(eval_result)
            
            results[principle.name] = {
                "score": score,
                "weight": principle.weight,
                "weighted_score": score * principle.weight,
                "feedback": eval_result
            }
        
        total_weight = sum(p.weight for p in self.principles)
        weighted_avg = sum(r["weighted_score"] for r in results.values()) / total_weight
        results["overall"] = weighted_avg
        
        return results
    
    def _parse_score(self, eval_text: str) -> float:
        """Extract score from evaluation text."""
        import re
        match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', eval_text)
        if match:
            return min(10.0, max(0.0, float(match.group(1))))
        return 5.0  # Default middle score if parsing fails
    
    def revise(self, response: str, context: str = "", 
               threshold: float = 7.0, max_attempts: int = 3) -> str:
        """Revise response until it meets constitutional standards."""
        current = response
        
        for attempt in range(max_attempts):
            evaluation = self.evaluate(current, context)
            
            if evaluation["overall"] >= threshold:
                return current
            
            # Find worst-scoring principle
            worst = min(
                [(k, v) for k, v in evaluation.items() if k != "overall"],
                key=lambda x: x[1]["weighted_score"] if isinstance(x[1], dict) else float('inf')
            )
            
            principle_name, result = worst
            principle = next(p for p in self.principles if p.name == principle_name)
            
            revision_prompt = f"""Original response: {current}

This response scored low on: {principle.name}
Feedback: {result['feedback']}

Please rewrite the response to better align with this principle:
{principle.description}

Provide only the revised response:"""
            
            current = self.bridge.generate(revision_prompt)
            self.revision_history.append({
                "attempt": attempt + 1,
                "principle_violated": principle_name,
                "revision": current[:200]
            })
        
        return current
    
    def filter(self, response: str, context: str = "") -> tuple:
        """Check if response passes constitutional filter."""
        evaluation = self.evaluate(response, context)
        passed = evaluation["overall"] >= 7.0
        
        violations = [
            name for name, result in evaluation.items()
            if name != "overall" and isinstance(result, dict) and result["score"] < 5.0
        ]
        
        return passed, violations, evaluation
