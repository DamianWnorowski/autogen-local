# 🤖 AutoGen Local Workflow Suite

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Zero-cost multi-agent AI workflow suite.** Runs 100% locally on your GPU with Ollama. No cloud APIs required.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent Crew** | Analyst, Researcher, Coder, Reviewer, Executor working together |
| **Code Review** | Security, Performance, Style, Architecture analysis |
| **Research Pipeline** | Query expansion, fact-checking, synthesis |
| **CI/CD Automation** | Lint, test, build, deploy with auto-fix |
| **Task Orchestrator** | Parallel execution with priorities and dependencies |
| **BFT Consensus** | Byzantine fault tolerant agent voting |
| **Genetic Evolution** | Evolve optimal prompts over generations |
| **Swarm Intelligence** | Ant colony optimization for solution search |
| **Self-Healing** | Auto-recovery from failures |
| **Persistent Memory** | SQLite + embeddings semantic search |
| **Distributed Comms** | Redis pub/sub, ZeroMQ mesh networking |
| **Observability** | Full tracing with metrics |
| **REPL Playground** | Interactive agent testing |
| **Web Dashboard** | Real-time monitoring UI |

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/DamianWnorowski/autogen-local.git
cd autogen-local

# 2. Setup (installs Ollama + models + dependencies)
chmod +x setup.sh && ./setup.sh

# 3. Activate and run
source venv/bin/activate
python main.py status
```

## 📋 Commands

```bash
python main.py status                    # Check system status
python main.py crew "Build a REST API"   # Run multi-agent crew
python main.py review ./src              # Code review
python main.py research "BFT consensus"  # Deep research
python main.py ci ./project              # Run CI/CD pipeline
python main.py orchestrate               # Parallel task demo
python main.py chat                      # Interactive chat
```

## 🐍 Python API

```python
from autogen_local import quick_crew, quick_review, quick_research, chat

# Multi-agent collaboration
result = quick_crew("Design a microservice architecture")

# Code review
findings = quick_review("./src")

# Research
report = quick_research("Byzantine fault tolerance")

# Simple chat
response = chat("Explain transformers")
```

## 📁 Project Structure

```
autogen_local/
├── config.py              # Global settings
├── local_bridge.py        # Ollama LLM wrapper
├── main.py                # CLI launcher
├── agents/
│   ├── base.py            # Agent factory
│   ├── crew.py            # Multi-agent crew
│   ├── swarm.py           # Swarm intelligence
│   ├── genetic.py         # Genetic prompt evolution
│   ├── bft_consensus.py   # Byzantine consensus
│   ├── decomposer.py      # Task decomposition
│   └── self_healing.py    # Self-healing system
├── workflows/
│   ├── code_review.py     # Code review pipeline
│   ├── research.py        # Research pipeline
│   ├── cicd.py            # CI/CD automation
│   └── orchestrator.py    # Task orchestration
├── memory/
│   ├── persistent.py      # SQLite + embeddings
│   └── context.py         # Context management
├── comms/
│   ├── redis_bus.py       # Redis pub/sub
│   └── zmq_mesh.py        # ZeroMQ mesh
├── observability/
│   └── tracing.py         # Distributed tracing
└── tools/
    ├── playground.py      # Interactive REPL
    ├── dashboard.py       # Web dashboard
    └── sandbox.py         # Code execution sandbox
```

## 🐳 Docker

```bash
# GPU-accelerated stack
docker compose up -d

# Run commands
docker compose exec autogen python main.py crew "task"
```

## 💰 Cost

**$0.00/forever** — Everything runs locally on your GPU.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
