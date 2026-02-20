# Use the official Python image
FROM python:3.12-bullseye

# Set environment variables at the beginning
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.2  \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/project/src" \
    VENV_PATH="/opt/project/src/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install dependencies
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev gettext curl graphviz \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 -

# Create appuser
RUN addgroup --gid 1024 appuser \
    && adduser --disabled-password --gecos "" --force-badname --ingroup appuser appuser

# Set WORKDIR to the project directory
WORKDIR /opt/project/src

# Copy only pyproject.toml and poetry.lock first (for better caching)
COPY --chown=appuser:appuser ./src/pyproject.toml ./src/poetry.lock /opt/project/src/

# Create project directory and set permissions
RUN mkdir -p /opt/project/src
RUN chown -R appuser:appuser /opt/project

# Ensure .pytest_cache with correct permissions
RUN mkdir -p /opt/project/src/.pytest_cache && \
    chown -R appuser:appuser /opt/project/src/.pytest_cache

# Switch to non-root user for Poetry operations
USER appuser

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# Accept build argument to determine environment
ARG ENVIRONMENT=production

# Install dependencies based on environment
RUN poetry config virtualenvs.in-project true \
    && if [ "$ENVIRONMENT" = "production" ] ; then \
        poetry install --no-root --only main \
        && poetry run pip list; \
    else \
        poetry install --no-root \
        && poetry run pip list; \
    fi

# Add this verification step
RUN poetry run python -c "import psycopg2; print('psycopg2 installed successfully')"

# Verify installation
RUN poetry run pip list

# Copy the rest of the application code
COPY --chown=appuser:appuser ./src /opt/project/src

# Switch back to root for copying files
USER root

# Copy entrypoint
COPY --chown=appuser:appuser ./docker/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

# Install gosu for step-down from root
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && gosu nobody true

# Setup data directory
RUN mkdir -p /data \
    && chown -R appuser:appuser /data \
    && chmod 775 /data \
    && chmod g+s /data

# This step is outside of entrypoint to avoid permission errors
RUN mkdir -p /data/staticfiles \
    && chown -R appuser:appuser /data/staticfiles \
    && chmod 775 /data/staticfiles

# Keep container as root, entrypoint will switch to appuser
WORKDIR /opt/project/src
ENTRYPOINT ["/entrypoint"]
