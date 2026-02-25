# Contributing Guide

## Branching Strategy

We use a **three-environment branching model**:

```
feature/*, bugfix/* ──► develop ──► staging ──► main
                         (dev)      (pre-prod)   (production)
```

All three branches are **protected**. Direct pushes are not allowed — all changes must go through a pull request.

## Branch Naming Conventions

Use the following prefixes for all branches:

| Prefix | Use case | Example |
|--------|----------|---------|
| `feature/` | New functionality | `feature/user-dashboard` |
| `bugfix/` | Bug fixes | `bugfix/login-redirect-loop` |
| `hotfix/` | Urgent production fixes | `hotfix/payment-timeout` |
| `task/` | Chores, refactoring, CI/CD, docs | `task/upgrade-django-5.2` |

Rules:
- Use lowercase, hyphen-separated names: `feature/add-user-search` (not `feature/AddUserSearch`)
- Include a ticket/issue number when applicable: `bugfix/GH-42-fix-email-validation`

## Commit Message Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/) format

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to catch issues before they reach CI.

### Setup

```bash
pip install pre-commit
pre-commit install
```
See `.pre-commit-config.yaml` for the full configuration.
