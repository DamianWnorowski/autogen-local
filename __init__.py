"""autogen-local: Zero-cost multi-agent AI workflow suite."""

__version__ = "0.1.0"
__author__ = "Damian Wnorowski"

from .local_bridge import LocalBridge
from .config import Config, DEFAULT_MODEL, CODE_MODEL

# Quick access functions
def chat(message: str, model: str = None) -> str:
    """Quick chat with default model."""
    bridge = LocalBridge(model=model or DEFAULT_MODEL)
    return bridge.chat(message)

def quick_crew(task: str, model: str = None) -> dict:
    """Run a quick multi-agent crew on a task."""
    from .workflows.orchestrator import Orchestrator
    orch = Orchestrator(model=model or DEFAULT_MODEL)
    return orch.run_crew(task)

def quick_review(path: str, model: str = None) -> dict:
    """Quick code review."""
    from .workflows.code_review import CodeReviewPipeline
    pipeline = CodeReviewPipeline(model=model or CODE_MODEL)
    return pipeline.review(path)

def quick_research(question: str, model: str = None) -> dict:
    """Quick research workflow."""
    from .workflows.research import ResearchWorkflow
    workflow = ResearchWorkflow(model=model or DEFAULT_MODEL)
    return workflow.research(question)

__all__ = [
    "LocalBridge",
    "Config",
    "DEFAULT_MODEL",
    "CODE_MODEL",
    "chat",
    "quick_crew",
    "quick_review",
    "quick_research",
    "__version__",
]
