# Getting Started with autogen-local

This guide will help you get the multi-agent system running locally.

## Prerequisites

- Python 3.9+
- Ollama installed and running
- GPU recommended (but not required)

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/DamianWnorowski/autogen-local.git
cd autogen-local
```

### 2. Set up environment

```bash
# Copy environment file
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Or use make
make install
```

### 3. Start Ollama

Make sure Ollama is running:

```bash
ollama serve
```

Pull a model if you haven't:

```bash
ollama pull llama3.2
ollama pull codellama  # for code tasks
```

### 4. Run the system

```bash
python main.py
```

## Configuration

Edit `.env` to customize:

- `OLLAMA_HOST` - Ollama server address (default: localhost:11434)
- `DEFAULT_MODEL` - Model for general tasks
- `CODE_MODEL` - Model for code generation
- `LOG_LEVEL` - Logging verbosity

## Next Steps

- Check out the agents in `agents/`
- Try different workflows in `workflows/`
- Run tests with `make test`
