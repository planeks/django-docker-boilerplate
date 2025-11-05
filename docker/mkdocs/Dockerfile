###############################################
# Base Image
###############################################
FROM python:3.12-slim AS python_base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.2  \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/code" \
    VENV_PATH="/code/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

###############################################
# Builder Image
###############################################
FROM python_base AS builder_base
RUN  apt-get update && \
    apt-get --no-install-recommends -y install \
    build-essential \
    ca-certificates \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 -

# Create directory and copy project files
WORKDIR $PYSETUP_PATH
COPY ./src/poetry.lock ./src/pyproject.toml ./

# Install dependencies with virtualenv in project
RUN poetry install --only docs

###############################################
# Production Image
###############################################
FROM python_base AS production

# Install curl for Poetry installation
RUN apt-get update && \
    apt-get --no-install-recommends -y install \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy the project files and virtual environment
COPY --from=builder_base $PYSETUP_PATH $PYSETUP_PATH
COPY --from=builder_base $POETRY_HOME $POETRY_HOME

WORKDIR $PYSETUP_PATH
COPY ./docs $PYSETUP_PATH/docs
COPY ./src $PYSETUP_PATH/src
COPY ./docker/mkdocs $PYSETUP_PATH
COPY ./docker/mkdocs/entrypoint $PYSETUP_PATH

# Add source directory to PYTHONPATH
ENV PYTHONPATH="${PYSETUP_PATH}/src:${PYTHONPATH}"

RUN chmod +x ./entrypoint

ENTRYPOINT [ "./entrypoint" ]