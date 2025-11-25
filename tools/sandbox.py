"""Sandboxed code execution environment."""
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Optional, Tuple


class Sandbox:
    """Safe execution environment for agent-generated code."""
    
    def __init__(self, timeout: int = 30, max_output: int = 10000):
        self.timeout = timeout
        self.max_output = max_output
        self.allowed_imports = {
            'math', 'json', 'datetime', 'collections',
            'itertools', 'functools', 'operator', 're',
            'string', 'random', 'statistics'
        }
    
    def execute_python(self, code: str) -> Tuple[bool, str, str]:
        """Execute Python code safely.
        
        Returns:
            Tuple of (success, stdout, stderr)
        """
        # Basic safety check
        dangerous = ['os.system', 'subprocess', 'eval(', 'exec(',
                     '__import__', 'open(', 'file(', 'input(']
        for pattern in dangerous:
            if pattern in code:
                return False, "", f"Blocked dangerous pattern: {pattern}"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = Path(tmpdir) / "script.py"
            script_path.write_text(code)
            
            try:
                result = subprocess.run(
                    ['python', str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tmpdir,
                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
                )
                stdout = result.stdout[:self.max_output]
                stderr = result.stderr[:self.max_output]
                success = result.returncode == 0
                return success, stdout, stderr
            except subprocess.TimeoutExpired:
                return False, "", f"Execution timed out after {self.timeout}s"
            except Exception as e:
                return False, "", str(e)
    
    def execute_shell(self, command: str) -> Tuple[bool, str, str]:
        """Execute shell command with restrictions."""
        # Very restricted - only allow safe commands
        allowed_commands = ['echo', 'date', 'pwd', 'whoami', 'ls']
        cmd_base = command.split()[0] if command.split() else ""
        
        if cmd_base not in allowed_commands:
            return False, "", f"Command '{cmd_base}' not in allowed list"
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return result.returncode == 0, result.stdout[:self.max_output], result.stderr[:self.max_output]
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def validate_code(self, code: str) -> Dict[str, any]:
        """Validate code without executing."""
        issues = []
        
        # Check for dangerous patterns
        dangerous_patterns = [
            ('os.system', 'System calls not allowed'),
            ('subprocess', 'Subprocess not allowed'),
            ('__import__', 'Dynamic imports not allowed'),
            ('eval(', 'Eval not allowed'),
            ('exec(', 'Exec not allowed'),
        ]
        
        for pattern, message in dangerous_patterns:
            if pattern in code:
                issues.append(message)
        
        # Try to compile
        try:
            compile(code, '<string>', 'exec')
            syntax_valid = True
        except SyntaxError as e:
            syntax_valid = False
            issues.append(f"Syntax error: {e}")
        
        return {
            'valid': len(issues) == 0,
            'syntax_valid': syntax_valid,
            'issues': issues
        }


def run_safe(code: str) -> str:
    """Quick helper to run code safely."""
    sandbox = Sandbox()
    success, stdout, stderr = sandbox.execute_python(code)
    if success:
        return stdout if stdout else "(no output)"
    return f"Error: {stderr}"
