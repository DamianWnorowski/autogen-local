"""Simple monitoring dashboard for agent runs."""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class Dashboard:
    """Basic dashboard for monitoring agent activity."""
    
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.metrics: Dict[str, List] = {
            "requests": [],
            "latencies": [],
            "errors": [],
            "tokens": []
        }
        self.start_time = time.time()
    
    def log_request(self, agent: str, prompt_tokens: int, completion_tokens: int, latency: float, success: bool = True):
        """Log a request."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency": latency,
            "success": success
        }
        self.metrics["requests"].append(entry)
        self.metrics["latencies"].append(latency)
        self.metrics["tokens"].append(entry["total_tokens"])
        if not success:
            self.metrics["errors"].append(entry)
    
    def get_stats(self) -> Dict:
        """Get current statistics."""
        total_requests = len(self.metrics["requests"])
        total_errors = len(self.metrics["errors"])
        
        return {
            "uptime_seconds": time.time() - self.start_time,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": total_errors / max(total_requests, 1),
            "avg_latency": sum(self.metrics["latencies"]) / max(len(self.metrics["latencies"]), 1),
            "total_tokens": sum(self.metrics["tokens"]),
            "requests_per_agent": self._count_by_agent()
        }
    
    def _count_by_agent(self) -> Dict[str, int]:
        """Count requests per agent."""
        counts = {}
        for req in self.metrics["requests"]:
            agent = req["agent"]
            counts[agent] = counts.get(agent, 0) + 1
        return counts
    
    def save_logs(self, filename: Optional[str] = None):
        """Save logs to file."""
        if filename is None:
            filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.log_dir / filename
        with open(filepath, 'w') as f:
            json.dump({
                "metrics": self.metrics,
                "stats": self.get_stats()
            }, f, indent=2)
        return str(filepath)
    
    def print_summary(self):
        """Print summary to console."""
        stats = self.get_stats()
        print(f"\n--- Dashboard Summary ---")
        print(f"Uptime: {stats['uptime_seconds']:.1f}s")
        print(f"Total requests: {stats['total_requests']}")
        print(f"Errors: {stats['total_errors']} ({stats['error_rate']*100:.1f}%)")
        print(f"Avg latency: {stats['avg_latency']*1000:.0f}ms")
        print(f"Total tokens: {stats['total_tokens']}")
        print(f"By agent: {stats['requests_per_agent']}")


# Global instance
_dashboard: Optional[Dashboard] = None

def get_dashboard() -> Dashboard:
    """Get or create global dashboard."""
    global _dashboard
    if _dashboard is None:
        _dashboard = Dashboard()
    return _dashboard
