#!/bin/bash
# ============================================================================
# Deployment Script for GitHub Actions
# ============================================================================
# Purpose: Deploy application to production
# Script runs by github actions, you are not supposed to start it manually.
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="${1:-compose.prod.yml}"
BRANCH="${2:-main}"
PROJECT_PATH="${3:-$(pwd)}"
PROJECT_PATH="${PROJECT_PATH/#\~/$HOME}"

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================================
# Pre-deployment Checks
# ============================================================================

log_info "Starting deployment process..."
log_info "Compose file: $COMPOSE_FILE"
log_info "Branch: $BRANCH"
log_info "Project path: $PROJECT_PATH"

cd "$PROJECT_PATH" || exit 1

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    log_error "Docker is not running!"
    exit 1
fi

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "Compose file not found: $COMPOSE_FILE"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    log_error ".env file not found!"
    log_error "Please create a .env file with required configuration."
    log_error "You can copy dev.env or prod.env as a starting point:"
    log_error "  cp dev.env .env  # for development"
    log_error "  cp prod.env .env  # for production"
    exit 1
fi

# Validate critical environment variables
log_info "Validating environment configuration..."

# Function to check if a value is a placeholder
is_placeholder() {
    local value="$1"
    [[ -z "$value" ]] || [[ "$value" =~ ^<.*>$ ]] || [[ "$value" == "secret_key" ]]
}

# Load .env file
set -a
source .env
set +a

# Check if critical secrets are configured
MISSING_SECRETS=false

if is_placeholder "${SECRET_KEY:-}"; then
    log_warning "SECRET_KEY is not configured in .env file"
    MISSING_SECRETS=true
fi

if is_placeholder "${POSTGRES_PASSWORD:-}"; then
    log_warning "POSTGRES_PASSWORD is not configured in .env file"
    MISSING_SECRETS=true
fi

# If secrets are missing, show instructions and exit gracefully
if [ "$MISSING_SECRETS" = true ]; then
    echo ""
    log_warning "========================================"
    log_warning "Environment Configuration Required"
    log_warning "========================================"
    echo ""
    log_info "The .env file needs to be configured before deployment can proceed."
    echo ""
    log_info "Steps to configure:"
    log_info "1. SSH to this server"
    log_info "2. Edit the .env file: nano $PROJECT_PATH/.env"
    log_info "3. Set the following required variables:"
    echo ""
    if is_placeholder "${SECRET_KEY:-}"; then
        log_info "   SECRET_KEY - Generate with:"
        log_info "   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
        echo ""
    fi
    if is_placeholder "${POSTGRES_PASSWORD:-}"; then
        log_info "   POSTGRES_PASSWORD - Use a secure random password"
        log_info "   Generate with: openssl rand -base64 32"
        echo ""
    fi
    log_info "4. Restart deploy."
    echo ""
    log_warning "========================================"
    log_warning "Deployment skipped - waiting for configuration"
    log_warning "========================================"
    exit 1
fi

# Check ALLOWED_HOSTS (for production)
if [ "$COMPOSE_FILE" = "compose.prod.yml" ]; then
    if [[ "${ALLOWED_HOSTS:-}" == "example.com" ]] || is_placeholder "${ALLOWED_HOSTS:-}"; then
        log_warning "ALLOWED_HOSTS is not properly configured!"
        log_warning "Please update ALLOWED_HOSTS in .env file with your actual domain."
    fi
fi

log_success "Environment validation passed!"

# Get current git commit for logging
CURRENT_COMMIT=$(git rev-parse HEAD)
log_info "Current commit: $CURRENT_COMMIT"

# ============================================================================
# Pull Latest Code
# ============================================================================

log_info "Pulling latest code from $BRANCH..."

# Stash any local changes (shouldn't be any in production)
if ! git diff-index --quiet HEAD --; then
    log_warning "Local changes detected, stashing..."
    git stash
fi

# Fetch and checkout
git fetch --all --prune
git checkout -B "$BRANCH" "origin/$BRANCH"
git reset --hard "origin/$BRANCH"

NEW_COMMIT=$(git rev-parse HEAD)
log_info "New commit: $NEW_COMMIT"

if [ "$CURRENT_COMMIT" = "$NEW_COMMIT" ]; then
    log_warning "No new changes detected. Current commit matches remote."
fi

# ============================================================================
# Build and Deploy
# ============================================================================

log_info "Building Docker images..."

if [ "$COMPOSE_FILE" = "compose.prod.yml" ]; then
    docker compose -f "$COMPOSE_FILE" --profile build build || {
        log_error "Build failed!"
        exit 1
    }
else
    docker compose -f "$COMPOSE_FILE" build || {
        log_error "Build failed!"
        exit 1
    }
fi

log_success "Build complete!"

log_info "Starting containers..."
docker compose -f "$COMPOSE_FILE" up -d || {
    log_error "Failed to start containers!"
    exit 1
}

log_success "Containers started!"

# ============================================================================
# Post-deployment Steps
# ============================================================================

log_info "Waiting for services to be ready..."

# Wait for postgres to be ready (up to 60 seconds)
log_info "Waiting for PostgreSQL to be ready..."
POSTGRES_READY=0
for i in {1..30}; do
    if docker compose -f "$COMPOSE_FILE" exec -T postgres bash -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' > /dev/null 2>&1; then
        POSTGRES_READY=1
        break
    fi
    sleep 2
done

if [ $POSTGRES_READY -eq 0 ]; then
    log_error "PostgreSQL failed to become ready in time!"
    exit 1
fi

log_success "PostgreSQL is ready!"

# Wait additional time for Django to start and run migrations
log_info "Waiting for Django to complete startup..."
sleep 15

# Check if containers are running (excluding build-only services like mkdocs and one-off run containers)
FAILED_SERVICES=$(docker compose -f "$COMPOSE_FILE" ps --status=exited --format '{{.Name}}' 2>/dev/null | grep -v -e 'docs' -e '\-run\-' || echo "")
if [ -n "$FAILED_SERVICES" ]; then
    log_error "Some services failed to start: $FAILED_SERVICES"
    exit 1
fi

log_success "All services running!"

# ============================================================================
# Health Check
# ============================================================================

log_info "Performing health check..."

# Check if Django is responding
HEALTH_CHECK_OUTPUT=$(docker compose -f "$COMPOSE_FILE" exec -T django bash -c "cd /opt/project/src && poetry run python manage.py check --deploy" 2>&1) || {
    log_error "Django health check failed!"
    log_error "Health check output:"
    echo "$HEALTH_CHECK_OUTPUT"
    log_error "Django container logs:"
    docker compose -f "$COMPOSE_FILE" logs --tail=50 django
    log_error "Rolling back"
    git checkout "$CURRENT_COMMIT"               # restore the code
    docker tag myapp:rollback myapp:latest       # restore the image
    docker compose -f "$COMPOSE_FILE" up -d      # restart previous containers
    docker image prune -f                        # clean up after rollback
    exit 1
}

log_info "Health check output:"
echo "$HEALTH_CHECK_OUTPUT"
log_success "Django health check passed!"

log_info "Cleaning up old Docker images..."
docker image prune -f

# ============================================================================
# Success
# ============================================================================

log_success "========================================"
log_success "Deployment completed successfully!"
log_success "========================================"
log_success "Commit: $NEW_COMMIT"
log_success "Time: $(date)"
log_success "========================================"

exit 0
