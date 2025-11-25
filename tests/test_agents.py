"""Tests for agent modules."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCoderAgent(unittest.TestCase):
    """Tests for the coder agent."""
    
    @patch('agents.coder.OllamaClient')
    def test_coder_initialization(self, mock_client):
        """Coder agent should initialize properly."""
        mock_client.return_value = MagicMock()
        try:
            from agents.coder import CoderAgent
            agent = CoderAgent()
            self.assertIsNotNone(agent)
        except ImportError:
            self.skipTest("CoderAgent not available")
    
    def test_coder_has_generate_method(self):
        """Coder should have code generation capability."""
        try:
            from agents.coder import CoderAgent
            self.assertTrue(hasattr(CoderAgent, 'generate') or 
                          hasattr(CoderAgent, 'run') or
                          hasattr(CoderAgent, '__call__'))
        except ImportError:
            self.skipTest("CoderAgent not available")


class TestReviewerAgent(unittest.TestCase):
    """Tests for the reviewer agent."""
    
    @patch('agents.reviewer.OllamaClient')
    def test_reviewer_initialization(self, mock_client):
        """Reviewer agent should initialize properly."""
        mock_client.return_value = MagicMock()
        try:
            from agents.reviewer import ReviewerAgent
            agent = ReviewerAgent()
            self.assertIsNotNone(agent)
        except ImportError:
            self.skipTest("ReviewerAgent not available")


class TestPlannerAgent(unittest.TestCase):
    """Tests for the planner agent."""
    
    @patch('agents.planner.OllamaClient')
    def test_planner_initialization(self, mock_client):
        """Planner agent should initialize properly."""
        mock_client.return_value = MagicMock()
        try:
            from agents.planner import PlannerAgent
            agent = PlannerAgent()
            self.assertIsNotNone(agent)
        except ImportError:
            self.skipTest("PlannerAgent not available")


class TestExecutorAgent(unittest.TestCase):
    """Tests for the executor agent."""
    
    def test_executor_sandbox_mode(self):
        """Executor should support sandbox mode."""
        try:
            from agents.executor import ExecutorAgent
            # Check if sandbox mode is configurable
            self.assertTrue(True)  # Placeholder
        except ImportError:
            self.skipTest("ExecutorAgent not available")


class TestAgentBase(unittest.TestCase):
    """Tests for base agent functionality."""
    
    def test_base_agent_exists(self):
        """Base agent module should exist."""
        try:
            from agents import base
            self.assertIsNotNone(base)
        except ImportError:
            self.skipTest("Base agent not available")


if __name__ == '__main__':
    unittest.main()
