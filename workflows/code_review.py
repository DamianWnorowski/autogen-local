"""Code review workflow using multi-agent collaboration."""
from typing import Optional, List
from dataclasses import dataclass
from local_bridge import LocalBridge


@dataclass
class ReviewComment:
    """A single review comment."""
    line: int
    severity: str  # info, warning, error
    category: str  # style, logic, security, performance
    message: str
    suggestion: Optional[str] = None


class CodeReviewWorkflow:
    """Multi-agent code review workflow."""
    
    def __init__(self, bridge: Optional[LocalBridge] = None):
        self.bridge = bridge or LocalBridge()
    
    def review(self, code: str, language: str = "python") -> dict:
        """Run full code review with multiple specialist agents."""
        results = {
            "style": self._style_review(code, language),
            "logic": self._logic_review(code, language),
            "security": self._security_review(code, language),
            "performance": self._performance_review(code, language)
        }
        
        # Aggregate all comments
        all_comments = []
        for category, comments in results.items():
            all_comments.extend(comments)
        
        return {
            "comments": all_comments,
            "summary": self._generate_summary(all_comments),
            "score": self._calculate_score(all_comments)
        }
    
    def _style_review(self, code: str, language: str) -> List[ReviewComment]:
        """Review code style and formatting."""
        prompt = f"""Review this {language} code for style issues:

```{language}
{code}
```

List style issues (formatting, naming, conventions).
Format each as: LINE:<num> ISSUE:<description> FIX:<suggestion>"""
        
        return self._parse_review(self.bridge.generate(prompt), "style")
    
    def _logic_review(self, code: str, language: str) -> List[ReviewComment]:
        """Review code logic and correctness."""
        prompt = f"""Review this {language} code for logic issues:

```{language}
{code}
```

Find bugs, edge cases, and logical errors.
Format each as: LINE:<num> ISSUE:<description> FIX:<suggestion>"""
        
        return self._parse_review(self.bridge.generate(prompt), "logic")
    
    def _security_review(self, code: str, language: str) -> List[ReviewComment]:
        """Review code for security vulnerabilities."""
        prompt = f"""Security review this {language} code:

```{language}
{code}
```

Find vulnerabilities (injection, auth, data exposure).
Format each as: LINE:<num> ISSUE:<description> FIX:<suggestion>"""
        
        return self._parse_review(self.bridge.generate(prompt), "security")
    
    def _performance_review(self, code: str, language: str) -> List[ReviewComment]:
        """Review code for performance issues."""
        prompt = f"""Review this {language} code for performance:

```{language}
{code}
```

Find inefficiencies and optimization opportunities.
Format each as: LINE:<num> ISSUE:<description> FIX:<suggestion>"""
        
        return self._parse_review(self.bridge.generate(prompt), "performance")
    
    def _parse_review(self, response: str, category: str) -> List[ReviewComment]:
        """Parse review response into structured comments."""
        comments = []
        for line in response.split('\n'):
            if 'LINE:' in line and 'ISSUE:' in line:
                try:
                    parts = line.split('LINE:')[1]
                    line_num = int(parts.split()[0])
                    issue = parts.split('ISSUE:')[1].split('FIX:')[0].strip()
                    fix = parts.split('FIX:')[1].strip() if 'FIX:' in parts else None
                    comments.append(ReviewComment(
                        line=line_num, severity="warning",
                        category=category, message=issue, suggestion=fix
                    ))
                except:
                    pass
        return comments
    
    def _generate_summary(self, comments: List[ReviewComment]) -> str:
        """Generate review summary."""
        by_category = {}
        for c in comments:
            by_category.setdefault(c.category, []).append(c)
        
        parts = [f"{cat}: {len(items)} issues" for cat, items in by_category.items()]
        return "Review complete. " + ", ".join(parts) if parts else "No issues found."
    
    def _calculate_score(self, comments: List[ReviewComment]) -> float:
        """Calculate code quality score (0-100)."""
        if not comments:
            return 100.0
        
        deductions = {"error": 10, "warning": 3, "info": 1}
        total_deduction = sum(deductions.get(c.severity, 2) for c in comments)
        return max(0.0, 100.0 - total_deduction)
