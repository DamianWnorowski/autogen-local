# autogen-local

Local multi-agent framework built on top of AutoGen + Ollama. Runs entirely on your own hardware.

I built this because I wanted to experiment with multi-agent workflows without paying for API calls. Works pretty well on a 3080 but should run on anything that can handle Ollama.

## what's in here

- multi-agent crews (analyst, coder, reviewer, etc working together)
- code review pipeline - catches security/perf/style issues
- research workflow - breaks down questions and synthesizes answers  
- task orchestration with parallel execution
- some experimental stuff (BFT consensus between agents, genetic prompt evolution)
- persistent memory using sqlite + embeddings
- redis/zmq support if you want distributed agents across machines

## setup

```bash
git clone https://github.com/DamianWnorowski/autogen-local.git
cd autogen-local

# this installs ollama, pulls models, sets up venv
chmod +x setup.sh && ./setup.sh

source venv/bin/activate
python main.py status
```

needs python 3.10+ and ollama. the setup script handles most of it.

## usage

```bash
# check if everything's working
python main.py status

# run the multi-agent crew on a task
python main.py crew "build a cli todo app"

# review some code
python main.py review ./src

# research something
python main.py research "how does raft consensus work"

# just chat
python main.py chat
```

or use it as a library:

```python
from autogen_local import quick_crew, quick_review, chat

result = quick_crew("design a rest api")
findings = quick_review("./myproject")
response = chat("explain transformers")
```

## structure

```
agents/       - agent definitions (crew, swarm, genetic, etc)
workflows/    - pipelines (code review, research, cicd)
memory/       - persistence layer
comms/        - distributed agent communication
tools/        - repl, dashboard, sandbox
```

## models

by default uses llama3:8b for general stuff and deepseek-coder for code tasks. you can change this in config.py or set env vars:

```bash
export DEFAULT_MODEL=mistral:7b
export CODE_MODEL=codellama:13b
```

## docker

```bash
docker compose up -d
docker compose exec autogen python main.py crew "your task"
```

## notes

- the bft consensus and genetic evolution stuff is experimental, might be buggy
- memory consolidation runs automatically but you can trigger it manually
- if ollama crashes the self-healing system should restart it

## license

mit
