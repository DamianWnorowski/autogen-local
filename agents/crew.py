"""Multi-agent crew for collaborative task execution."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import json

from local_bridge import ollama, Message
from config import config


class Role(Enum):
    ANALYST = "analyst"
    CODER = "coder"
    REVIEWER = "reviewer"
    PLANNER = "planner"
    EXECUTOR = "executor"


@dataclass
class Agent:
    """Single agent in the crew."""
    name: str
    role: Role
    system_prompt: str
    model: Optional[str] = None
    history: List[Message] = field(default_factory=list)
    
    def think(self, prompt: str) -> str:
        """Generate response from agent."""
        messages = [
            Message(role="system", content=self.system_prompt),
            *self.history,
            Message(role="user", content=prompt)
        ]
        response = ollama.chat(messages, model=self.model)
        self.history.append(Message(role="user", content=prompt))
        self.history.append(Message(role="assistant", content=response))
        return response
    
    def clear_history(self):
        self.history = []


class Crew:
    """Multi-agent crew that collaborates on tasks."""
    
    def __init__(self):
        self.agents = self._create_default_agents()
        self.conversation_log = []
    
    def _create_default_agents(self) -> Dict[Role, Agent]:
        return {
            Role.ANALYST: Agent(
                name="Analyst",
                role=Role.ANALYST,
                system_prompt="You are an analyst. Break down problems, identify requirements, and provide clear analysis. Be thorough but concise."
            ),
            Role.CODER: Agent(
                name="Coder", 
                role=Role.CODER,
                system_prompt="You are an expert programmer. Write clean, efficient code with proper error handling. Use best practices.",
                model=config.ollama.code_model
            ),
            Role.REVIEWER: Agent(
                name="Reviewer",
                role=Role.REVIEWER,
                system_prompt="You are a code reviewer. Check for bugs, security issues, performance problems, and style. Be constructive."
            ),
            Role.PLANNER: Agent(
                name="Planner",
                role=Role.PLANNER,
                system_prompt="You are a project planner. Create actionable plans with clear steps and dependencies."
            ),
        }
    
    def run(self, task: str, max_rounds: int = 3) -> str:
        """Run the crew on a task."""
        # Step 1: Analyst breaks down the task
        analysis = self.agents[Role.ANALYST].think(
            f"Analyze this task and identify key requirements:\n{task}"
        )
        self._log("Analyst", analysis)
        
        # Step 2: Planner creates execution plan
        plan = self.agents[Role.PLANNER].think(
            f"Based on this analysis, create an execution plan:\n{analysis}"
        )
        self._log("Planner", plan)
        
        # Step 3: Coder implements
        code = self.agents[Role.CODER].think(
            f"Implement according to this plan:\n{plan}\n\nOriginal task: {task}"
        )
        self._log("Coder", code)
        
        # Step 4: Reviewer checks
        review = self.agents[Role.REVIEWER].think(
            f"Review this implementation:\n{code}\n\nOriginal requirements:\n{analysis}"
        )
        self._log("Reviewer", review)
        
        # Compile final result
        result = f"## Analysis\n{analysis}\n\n## Plan\n{plan}\n\n## Implementation\n{code}\n\n## Review\n{review}"
        return result
    
    def _log(self, agent: str, message: str):
        self.conversation_log.append({"agent": agent, "message": message})
    
    def get_log(self) -> List[Dict[str, str]]:
        return self.conversation_log
    
    def clear(self):
        for agent in self.agents.values():
            agent.clear_history()
        self.conversation_log = []
