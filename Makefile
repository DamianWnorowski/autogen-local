.PHONY: install test lint format run docker-build docker-run clean help

install:
	pip install -r requirements.txt
	pip install -e .[dev]

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ -v --cov=. --cov-report=html

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --statistics

format:
	black .

run:
	python main.py

docker-build:
	docker build -t autogen-local .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov

setup:
	cp .env.example .env
	./setup.sh

help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linter"
	@echo "  format       - Format code with black"
	@echo "  run          - Run main application"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  clean        - Remove cache files"
	@echo "  setup        - Initial setup"
