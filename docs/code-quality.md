# Code quality

This project uses automated linting, formatting, security scanning, and Poetry-based dependency management for the Python backend.

## Tools

### Python (backend)

- **Ruff** handles both linting and formatting. Configuration lives in `src/pyproject.toml` under `[tool.ruff]`.
- **pip-audit** scans Python dependencies for known vulnerabilities in CI.

## Dependency management

This project uses [Poetry](https://python-poetry.org/) (v1.8.2) to manage Python dependencies.
All dependencies are declared in `src/pyproject.toml` and locked in `src/poetry.lock`.
Three dependency groups are defined: **main**, **dev**, and **docs**.

### Adding a dependency

```bash
$ docker compose -f compose.dev.yml run --rm django add <package>
```

To pin a specific version:

```bash
$ docker compose -f compose.dev.yml run --rm django add "django>=5.1,<5.2"
```

### Updating a dependency

```bash
$ docker compose -f compose.dev.yml exec django poetry update <package>  # update a specific package
$ docker compose -f compose.dev.yml exec django poetry update            # update all packages
$ docker compose -f compose.dev.yml exec django poetry show --outdated   # list outdated packages
```

### Removing a dependency

```bash
$ docker compose -f compose.dev.yml exec django poetry remove <package>
```

> Always commit both `pyproject.toml` and `poetry.lock` after making changes.
> After adding or removing dependencies, rebuild the Docker image: `docker compose -f compose.dev.yml build django`.

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
