# Linting & Code Quality — Quick Reference

## Daily workflow

```bash
# Before committing (automatic via pre-commit):
make lint

# If linters complain:
make format

# Run tests:
make test

# Full CI check (lint + test):
make check
```

## Install once

```bash
cd backend
pip install -e ".[dev]"
pre-commit install
```

## All commands

```bash
make install      # Install deps + hooks
make lint         # ruff + flake8 + mypy
make format       # Auto-fix with black + isort + ruff
make test         # Pytest with coverage
make test-fast    # Pytest without coverage
make pre-commit   # Run all pre-commit hooks
make clean        # Remove build/cache artifacts
make check        # lint + test (CI-ready)
```

## Tools in use

- **black** (formatter) — line length 100
- **isort** (import sorter) — black-compatible
- **flake8** (PEP 8 checker) — line length 100
- **ruff** (fast linter) — replaces flake8 + pyupgrade + more
- **mypy** (type checker) — strict mode
- **pre-commit** (git hooks) — runs on every commit

## Config files

- `pyproject.toml` → black, isort, ruff, mypy, pytest
- `.flake8` → flake8-specific settings
- `.pre-commit-config.yaml` → pre-commit hooks
- `Makefile` → all commands

See [`docs/LINTING.md`](./LINTING.md) for full documentation.
