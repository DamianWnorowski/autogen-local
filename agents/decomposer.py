"""Task decomposition for complex problems."""
from dataclasses import dataclass
from typing import List, Dict, Any
import json

from local_bridge import ollama


@dataclass
class SubTask:
    """A decomposed subtask."""
    id: str
    description: str
    dependencies: List[str]
    priority: int = 0
    status: str = "pending"
    result: str = ""


class TaskDecomposer:
    """Decompose complex tasks into subtasks."""
    
    def __init__(self):
        self.subtasks: Dict[str, SubTask] = {}
    
    def decompose(self, task: str, max_depth: int = 2) -> List[SubTask]:
        """Break task into subtasks."""
        prompt = f"""Break this task into 3-5 smaller subtasks. Return JSON array:
[{{"id": "1", "description": "...", "dependencies": [], "priority": 1}}]

Task: {task}"""
        
        response = ollama.generate(prompt)
        
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                tasks_data = json.loads(json_match.group())
                for t in tasks_data:
                    subtask = SubTask(
                        id=t.get("id", str(len(self.subtasks))),
                        description=t.get("description", ""),
                        dependencies=t.get("dependencies", []),
                        priority=t.get("priority", 0)
                    )
                    self.subtasks[subtask.id] = subtask
        except json.JSONDecodeError:
            # Fallback: single subtask
            self.subtasks["1"] = SubTask(id="1", description=task, dependencies=[])
        
        return list(self.subtasks.values())
    
    def execute_order(self) -> List[SubTask]:
        """Get execution order based on dependencies."""
        executed = set()
        order = []
        
        while len(order) < len(self.subtasks):
            for st in self.subtasks.values():
                if st.id in executed:
                    continue
                if all(d in executed for d in st.dependencies):
                    order.append(st)
                    executed.add(st.id)
        
        return order
    
    def execute_all(self) -> Dict[str, str]:
        """Execute all subtasks in order."""
        results = {}
        for subtask in self.execute_order():
            context = "\n".join([f"Completed: {self.subtasks[d].result}" for d in subtask.dependencies if d in self.subtasks])
            prompt = f"{context}\n\nNow do: {subtask.description}" if context else subtask.description
            subtask.result = ollama.generate(prompt)
            subtask.status = "done"
            results[subtask.id] = subtask.result
        return results
