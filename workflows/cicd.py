"""CI/CD workflow for automated testing and deployment."""
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass
from enum import Enum
from local_bridge import LocalBridge


class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result of a CI/CD stage."""
    name: str
    status: StageStatus
    output: str
    duration: float
    errors: List[str]


class CICDWorkflow:
    """Multi-agent CI/CD pipeline workflow."""
    
    def __init__(self, bridge: Optional[LocalBridge] = None):
        self.bridge = bridge or LocalBridge()
        self.stages = []
        self.results = []
    
    def add_stage(self, name: str, handler: Callable, 
                  depends_on: Optional[List[str]] = None):
        """Add a stage to the pipeline."""
        self.stages.append({
            "name": name,
            "handler": handler,
            "depends_on": depends_on or []
        })
    
    def run(self, context: dict) -> dict:
        """Execute the CI/CD pipeline."""
        self.results = []
        
        for stage in self.stages:
            # Check dependencies
            if not self._deps_passed(stage["depends_on"]):
                result = StageResult(
                    name=stage["name"],
                    status=StageStatus.SKIPPED,
                    output="Dependencies not met",
                    duration=0.0,
                    errors=[]
                )
            else:
                result = self._run_stage(stage, context)
            
            self.results.append(result)
            
            if result.status == StageStatus.FAILED:
                break
        
        return {
            "success": all(r.status in [StageStatus.PASSED, StageStatus.SKIPPED] 
                          for r in self.results),
            "stages": self.results,
            "summary": self._generate_summary()
        }
    
    def _deps_passed(self, deps: List[str]) -> bool:
        """Check if all dependencies passed."""
        for dep in deps:
            dep_result = next((r for r in self.results if r.name == dep), None)
            if not dep_result or dep_result.status != StageStatus.PASSED:
                return False
        return True
    
    def _run_stage(self, stage: dict, context: dict) -> StageResult:
        """Execute a single stage."""
        import time
        start = time.time()
        errors = []
        
        try:
            output = stage["handler"](context, self.bridge)
            status = StageStatus.PASSED
        except Exception as e:
            output = str(e)
            status = StageStatus.FAILED
            errors.append(str(e))
        
        return StageResult(
            name=stage["name"],
            status=status,
            output=str(output)[:1000],
            duration=time.time() - start,
            errors=errors
        )
    
    def _generate_summary(self) -> str:
        """Generate pipeline summary."""
        passed = sum(1 for r in self.results if r.status == StageStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == StageStatus.FAILED)
        total = len(self.results)
        
        return f"Pipeline: {passed}/{total} passed, {failed} failed"


# Default CI/CD stages
def lint_stage(ctx: dict, bridge: LocalBridge) -> str:
    """Lint code using LLM analysis."""
    code = ctx.get("code", "")
    prompt = f"""Analyze this code for linting issues:
{code[:2000]}

List any style, formatting, or convention issues."""
    return bridge.generate(prompt)


def test_stage(ctx: dict, bridge: LocalBridge) -> str:
    """Generate and analyze tests."""
    code = ctx.get("code", "")
    prompt = f"""For this code, identify what tests should be written:
{code[:2000]}

Describe test cases needed for full coverage."""
    return bridge.generate(prompt)


def security_stage(ctx: dict, bridge: LocalBridge) -> str:
    """Security analysis."""
    code = ctx.get("code", "")
    prompt = f"""Security audit this code:
{code[:2000]}

Identify vulnerabilities and security concerns."""
    return bridge.generate(prompt)
