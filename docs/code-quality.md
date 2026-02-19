# Code quality

This project uses automated linting, formatting, and security scanning for the Python backend.

## Tools

### Python (backend)

- **Ruff** handles both linting and formatting. Configuration lives in `src/pyproject.toml` under `[tool.ruff]`.
- **pip-audit** scans Python dependencies for known vulnerabilities in CI.

## Running locally

```bash
docker compose -f compose.dev.yml exec django ruff check .          # lint
docker compose -f compose.dev.yml exec django ruff check --fix .    # lint and auto-fix
docker compose -f compose.dev.yml exec django ruff format .         # format
docker compose -f compose.dev.yml exec django ruff format --check . # check formatting without changes
```

## Pre-commit hooks

The project includes a `.pre-commit-config.yaml` that runs Ruff automatically before each commit. To set it up:

```bash
pip install pre-commit
pre-commit install
```

After that, every `git commit` will run the hooks on staged files. To run them manually on all files:

```bash
pre-commit run --all-files
```

## CI pipeline

The GitHub Actions CI workflow (`.github/workflows/ci.yml`) runs three jobs:

1. **check_migration_conflicts** -- Detects duplicate migration prefixes between PR and base branch (PR only)
2. **lint-backend** -- Ruff check, Ruff format check, pip-audit
3. **test-backend** -- Django tests in Docker (runs after lint-backend passes)

Staging and production deploys require CI to pass first.

## Dependabot

Dependabot (`.github/dependabot.yml`) opens monthly pull requests for:

- Python dependencies (`pip` ecosystem, `src/` directory)
- GitHub Actions versions (`github-actions` ecosystem)
