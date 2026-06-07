.PHONY: help install lint format test clean pre-commit

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies + pre-commit hooks
	pip install -e ".[dev]"
	pre-commit install

lint:  ## Run all linters (ruff, flake8, mypy)
	@echo "→ Running ruff..."
	ruff check app tests
	@echo "\n→ Running flake8..."
	flake8 app tests
	@echo "\n→ Running mypy..."
	mypy app
	@echo "\n✓ All linters passed"

format:  ## Auto-format code with black + isort + ruff
	@echo "→ Running isort..."
	isort app tests
	@echo "→ Running black..."
	black app tests
	@echo "→ Running ruff --fix..."
	ruff check --fix app tests
	@echo "\n✓ Code formatted"

test:  ## Run tests with coverage
	pytest -v --cov=app --cov-report=term-missing --cov-report=html

test-fast:  ## Run tests without coverage
	pytest -v

pre-commit:  ## Run pre-commit on all files
	pre-commit run --all-files

clean:  ## Remove build artifacts, cache, coverage
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

check: lint test  ## Run linters + tests (CI-ready)
