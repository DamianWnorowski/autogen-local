"""Self-healing agent that monitors and recovers from failures."""
import time
import subprocess
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
import threading

from local_bridge import ollama


@dataclass
class HealthCheck:
    name: str
    check_fn: Callable[[], bool]
    recovery_fn: Callable[[], None]
    interval: int = 30
    last_check: float = 0
    failures: int = 0


class SelfHealingAgent:
    """Agent that monitors system health and auto-recovers."""
    
    def __init__(self):
        self.checks: Dict[str, HealthCheck] = {}
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default health checks."""
        self.register(
            "ollama",
            check_fn=lambda: ollama.is_healthy(),
            recovery_fn=self._recover_ollama
        )
    
    def register(self, name: str, check_fn: Callable, recovery_fn: Callable, interval: int = 30):
        """Register a health check."""
        self.checks[name] = HealthCheck(
            name=name, check_fn=check_fn, recovery_fn=recovery_fn, interval=interval
        )
    
    def _recover_ollama(self):
        """Try to restart Ollama."""
        try:
            subprocess.run(["ollama", "serve"], start_new_session=True, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)
        except Exception as e:
            print(f"Failed to restart Ollama: {e}")
    
    def check_all(self) -> Dict[str, bool]:
        """Run all health checks."""
        results = {}
        for name, check in self.checks.items():
            try:
                healthy = check.check_fn()
                results[name] = healthy
                if not healthy:
                    check.failures += 1
                    if check.failures >= 3:
                        print(f"Running recovery for {name}")
                        check.recovery_fn()
                        check.failures = 0
                else:
                    check.failures = 0
            except Exception as e:
                results[name] = False
                check.failures += 1
        return results
    
    def start_monitoring(self):
        """Start background monitoring."""
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def _monitor_loop(self):
        while self.running:
            self.check_all()
            time.sleep(10)
