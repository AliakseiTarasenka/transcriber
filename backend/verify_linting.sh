#!/bin/bash
# Verify linting setup is working correctly

set -e

echo "🔍 Verifying linting setup..."
echo

cd "$(dirname "$0")"

# Check tools are installed
echo "✓ Checking tool versions..."
black --version | head -1
isort --version | head -1
flake8 --version | head -1
ruff --version
mypy --version
pre-commit --version
echo

# Run all linters
echo "✓ Running all linters..."
make lint
echo

# Run tests
echo "✓ Running tests..."
make test-fast
echo

# Check pre-commit
echo "✓ Verifying pre-commit hooks..."
pre-commit run --all-files
echo

echo "✅ All checks passed! Linting setup is working correctly."
