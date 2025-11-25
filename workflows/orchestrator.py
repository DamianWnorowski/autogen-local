"""Workflow orchestrator for managing multiple workflows."""
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from local_bridge import LocalBridge


class WorkflowStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowRun:
    """Record of a workflow execution."""
    workflow_id: str
    workflow_type: str
    status: WorkflowStatus
    result: Optional[dict]
    error: Optional[str]


class WorkflowOrchestrator:
    """Orchestrates multiple workflow types."""
    
    def __init__(self, bridge: Optional[LocalBridge] = None):
        self.bridge = bridge or LocalBridge()
        self.workflows: Dict[str, Any] = {}
        self.run_history: List[WorkflowRun] = []
        self._run_counter = 0
    
    def register(self, name: str, workflow):
        """Register a workflow by name."""
        self.workflows[name] = workflow
    
    def run(self, workflow_name: str, **kwargs) -> dict:
        """Execute a registered workflow."""
        if workflow_name not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        self._run_counter += 1
        run_id = f"run_{self._run_counter}"
        
        workflow = self.workflows[workflow_name]
        
        try:
            # Determine the entry method
            if hasattr(workflow, 'run'):
                result = workflow.run(**kwargs)
            elif hasattr(workflow, 'execute'):
                result = workflow.execute(**kwargs)
            elif hasattr(workflow, 'review'):
                result = workflow.review(**kwargs)
            elif hasattr(workflow, 'research'):
                result = workflow.research(**kwargs)
            else:
                result = workflow(**kwargs)
            
            run_record = WorkflowRun(
                workflow_id=run_id,
                workflow_type=workflow_name,
                status=WorkflowStatus.COMPLETED,
                result=result,
                error=None
            )
        except Exception as e:
            run_record = WorkflowRun(
                workflow_id=run_id,
                workflow_type=workflow_name,
                status=WorkflowStatus.FAILED,
                result=None,
                error=str(e)
            )
        
        self.run_history.append(run_record)
        
        return {
            "run_id": run_id,
            "status": run_record.status.value,
            "result": run_record.result,
            "error": run_record.error
        }
    
    def run_parallel(self, workflow_runs: List[dict]) -> List[dict]:
        """Run multiple workflows (sequential for now, parallel later)."""
        results = []
        for run_config in workflow_runs:
            name = run_config.pop("workflow")
            result = self.run(name, **run_config)
            results.append(result)
        return results
    
    def get_history(self, limit: int = 10) -> List[dict]:
        """Get recent workflow runs."""
        recent = self.run_history[-limit:]
        return [
            {
                "id": r.workflow_id,
                "type": r.workflow_type,
                "status": r.status.value,
                "has_result": r.result is not None,
                "has_error": r.error is not None
            }
            for r in reversed(recent)
        ]
    
    def list_workflows(self) -> List[str]:
        """List available workflows."""
        return list(self.workflows.keys())
