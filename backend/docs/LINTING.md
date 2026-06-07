# Code Quality & Linting

This project uses multiple linters and formatters to ensure code quality, consistency, and maintainability.

## Tools

| Tool | Purpose | Config |
|---|---|---|
| **black** | Opinionated code formatter | `pyproject.toml` → `[tool.black]` |
| **isort** | Import statement sorter (black-compatible) | `pyproject.toml` → `[tool.isort]` |
| **flake8** | PEP 8 style guide enforcement | `.flake8` |
| **ruff** | Fast linter (replaces flake8 + isort + more) | `pyproject.toml` → `[tool.ruff]` |
| **mypy** | Static type checker | `pyproject.toml` → `[tool.mypy]` |
| **pre-commit** | Git hook manager | `.pre-commit-config.yaml` |

## Quick Start

### Install tools
```bash
cd backend
pip install -e ".[dev]"
pre-commit install
```

### Run linters manually
```bash
# All linters at once
make lint

# Individual tools
ruff check app tests
flake8 app tests
mypy app
```

### Auto-format code
```bash
make format
# Or individually:
black app tests
isort app tests
ruff check --fix app tests
```

### Run pre-commit on all files
```bash
make pre-commit
# Or:
pre-commit run --all-files
```

## Configuration Details

### Black
- Line length: **100** (wider than PEP 8's 79 for modern screens)
- Target: Python 3.12+
- Preserves double quotes (follows black's defaults)

### isort
- Profile: `black` (ensures compatibility)
- Line length: 100
- Ensures trailing commas and parentheses for multi-line imports

### Flake8
- Line length: 100
- Ignores:
  - `E203` — whitespace before `:` (black adds this for readability)
  - `W503` — line break before binary operator (PEP 8 updated, black follows new style)
- Complexity: max 10 (catches overly complex functions)
- Per-file ignores:
  - `__init__.py` → allows unused imports (re-exports)
  - `tests/*` → allows long lines, unused imports

### Ruff
Modern, fast linter written in Rust. Covers:
- **E/W** — pycodestyle (PEP 8 errors/warnings)
- **F** — pyflakes (unused imports, undefined names)
- **I** — isort (import ordering)
- **N** — pep8-naming (function/class naming conventions)
- **UP** — pyupgrade (modernize syntax for Python 3.12+)
- **B** — flake8-bugbear (common bugs)
- **C4** — flake8-comprehensions (better list/dict comprehensions)
- **SIM** — flake8-simplify (simplify complex expressions)
- **RUF** — ruff-specific rules

Ignored rules:
- `E203` — black compatibility
- `UP007` — `Union[X, Y]` vs. `X | Y` (Union is clearer for discriminated unions)
- `UP046` — `Generic[T]` vs. `class Foo[T]` (PEP 695 syntax not yet widely adopted)
- `RUF001` — ambiguous unicode (intentional: CJK punctuation for i18n)

### Mypy
- `strict = true` — maximum type safety
- `ignore_missing_imports = true` — third-party libraries without type stubs are allowed
- Python version: 3.12

Known suppressions:
- `app/core/logging.py` → `structlog.BoundLogger` is dynamically generated
- `app/main.py` → `lifespan()` yield type is complex (contextmanager + async)

## CI Integration

GitHub Actions (`.github/workflows/ci.yml`) runs:
1. **Lint job** — ruff, flake8, black (check-only), isort (check-only), mypy
2. **Test job** — pytest with coverage report → Codecov

Both jobs run on `push` to `main`/`develop` and on all PRs.

## Pre-commit Hooks

Installed with `pre-commit install`. Runs on **every commit**:

1. **isort** — sort imports
2. **black** — format code
3. **flake8** — catch style violations
4. **ruff** — fast linting + auto-fix
5. **mypy** — type check
6. **Standard hooks** — trailing whitespace, EOF newlines, YAML/TOML syntax, debug statements

To skip hooks (e.g. for WIP commits):
```bash
git commit --no-verify -m "WIP: work in progress"
```

## Makefile Commands

| Command | Description |
|---|---|
| `make install` | Install deps + pre-commit hooks |
| `make lint` | Run ruff + flake8 + mypy |
| `make format` | Auto-format with isort + black + ruff --fix |
| `make test` | Run tests with coverage |
| `make test-fast` | Run tests without coverage (faster) |
| `make pre-commit` | Run pre-commit on all files |
| `make clean` | Remove build artifacts, cache, coverage |
| `make check` | `lint` + `test` (CI-ready) |

## IDE Integration

### PyCharm / IntelliJ
1. **Black:** Settings → Tools → Black → Enable "On save"
2. **isort:** Settings → Tools → Actions on Save → Enable "Optimize imports" + use isort
3. **Flake8:** Settings → Editor → Inspections → Enable "Flake8" inspection
4. **Mypy:** Install "Mypy" plugin → Settings → Mypy → Enable

### VS Code
Install extensions:
- `ms-python.black-formatter`
- `ms-python.isort`
- `ms-python.flake8`
- `ms-python.mypy-type-checker`
- `charliermarsh.ruff`

Add to `.vscode/settings.json`:
```json
{
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "ruff.lint.run": "onSave"
}
```

## Common Issues

### `black` and `flake8` disagree on line breaks
**Solution:** This shouldn't happen with our config. If it does, black wins — add the violation to `.flake8` → `extend-ignore`.

### Mypy complains about missing stubs
**Solution:** Install type stubs: `pip install types-<package>` or add to `pyproject.toml` → `[tool.mypy]` → `ignore_missing_imports = true`.

### Pre-commit is too slow
**Solution:** Only run changed files by default (automatic). For full runs, `pre-commit` uses cached environments. First run is slow; subsequent runs are fast.

### Ruff and flake8 report the same issues
**Solution:** Pick one. Ruff is faster and more comprehensive. You can disable flake8 if you prefer ruff-only (remove from `Makefile` and `.pre-commit-config.yaml`).

## Ignoring Rules

### Per-file (flake8)
Edit `.flake8`:
```ini
per-file-ignores =
    specific_file.py:E501
```

### Per-line (flake8)
```python
long_line = "..." # noqa: E501
```

### Per-file (ruff)
Edit `pyproject.toml`:
```toml
[tool.ruff.lint.per-file-ignores]
"specific_file.py" = ["E501"]
```

### Per-line (ruff)
```python
long_line = "..."  # noqa: E501
```

### Mypy
```python
def tricky() -> Any:  # type: ignore[return-value]
    ...
```

---

**Bottom line:** Run `make lint` before every PR. All checks must pass in CI.
