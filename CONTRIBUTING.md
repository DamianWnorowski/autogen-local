# Contributing to autogen-local

Thanks for your interest in contributing.

## Getting Started

1. Fork the repo
2. Clone your fork
3. Create a branch for your changes
4. Make your changes
5. Run tests: `make test`
6. Submit a PR

## Development Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/autogen-local.git
cd autogen-local

# Install dependencies
make install

# Copy env file
cp .env.example .env

# Run tests
make test
```

## Code Style

- Use black for formatting: `make format`
- Run linter before committing: `make lint`
- Write tests for new features

## Pull Requests

- Keep PRs focused on a single change
- Include tests if adding new functionality
- Update docs if needed
- Use clear commit messages

## Issues

Feel free to open issues for:
- Bug reports
- Feature requests
- Questions

## Local Testing

Make sure Ollama is running locally before running tests that require it.

```bash
# Start Ollama
ollama serve

# In another terminal, run tests
make test
```
