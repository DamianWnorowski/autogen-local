"""Recursive self-improvement agent."""
from typing import Optional, Callable, List
from dataclasses import dataclass, field
from local_bridge import LocalBridge


@dataclass
class ImprovementRound:
    """Record of a single improvement iteration."""
    round_num: int
    input_text: str
    output_text: str
    score: float
    feedback: str


class RecursiveImprover:
    """Agent that iteratively improves outputs through self-critique."""
    
    def __init__(self, bridge: Optional[LocalBridge] = None,
                 max_rounds: int = 5, target_score: float = 8.0):
        self.bridge = bridge or LocalBridge()
        self.max_rounds = max_rounds
        self.target_score = target_score
        self.history: List[ImprovementRound] = []
    
    def improve(self, initial_output: str, task_description: str,
                scorer: Optional[Callable] = None) -> str:
        """Iteratively improve output until target score or max rounds."""
        current = initial_output
        scorer = scorer or self._default_scorer
        
        for round_num in range(self.max_rounds):
            score = scorer(current, task_description)
            
            if score >= self.target_score:
                self._log_round(round_num, initial_output, current, score, "Target reached")
                return current
            
            critique = self._critique(current, task_description)
            improved = self._apply_critique(current, critique, task_description)
            
            self._log_round(round_num, current, improved, score, critique)
            current = improved
        
        return current
    
    def _default_scorer(self, output: str, task: str) -> float:
        """Score output quality from 0-10."""
        prompt = f"""Task: {task}

Output to evaluate:
{output}

Rate this output from 0-10 based on:
- Correctness and accuracy
- Completeness
- Clarity and organization
- Relevance to task

Respond with just the numeric score:"""
        
        result = self.bridge.generate(prompt)
        try:
            score = float(result.strip().split()[0])
            return min(10.0, max(0.0, score))
        except:
            return 5.0
    
    def _critique(self, output: str, task: str) -> str:
        """Generate constructive critique of the output."""
        prompt = f"""Task: {task}

Current output:
{output}

Provide specific, actionable critique. Focus on:
1. What's missing or incorrect
2. What could be clearer
3. Specific improvements to make

Be concise and direct:"""
        
        return self.bridge.generate(prompt)
    
    def _apply_critique(self, output: str, critique: str, task: str) -> str:
        """Generate improved version based on critique."""
        prompt = f"""Task: {task}

Original output:
{output}

Critique to address:
{critique}

Write an improved version that addresses the critique.
Provide only the improved output:"""
        
        return self.bridge.generate(prompt)
    
    def _log_round(self, round_num: int, inp: str, out: str, 
                   score: float, feedback: str):
        """Log improvement round."""
        self.history.append(ImprovementRound(
            round_num=round_num,
            input_text=inp[:500],
            output_text=out[:500],
            score=score,
            feedback=feedback[:200]
        ))
    
    def get_improvement_report(self) -> dict:
        """Get summary of improvement process."""
        if not self.history:
            return {"status": "no_runs"}
        
        scores = [r.score for r in self.history]
        return {
            "total_rounds": len(self.history),
            "initial_score": scores[0],
            "final_score": scores[-1],
            "improvement": scores[-1] - scores[0],
            "rounds": [
                {"round": r.round_num, "score": r.score, "feedback": r.feedback}
                for r in self.history
            ]
        }
