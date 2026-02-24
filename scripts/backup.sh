#!/bin/bash
# ============================================================================
# Weekly Database Backup Script
# ============================================================================
# Creates database backup inside postgres container, cleans up old backups.
# Optionally backs up media files when --media flag is provided.
#
# Usage: ./backup.sh [compose_file] [project_path] [retention_days] [--media media_backup_dir]
# Example: ./backup.sh compose.prod.yml /home/appuser/projects/django_app 30
# Example: ./backup.sh compose.prod.yml /home/appuser/projects/django_app 30 --media /home/appuser/backups/media
# ============================================================================

set -euo pipefail

COMPOSE_FILE="${1:-compose.prod.yml}"
PROJECT_PATH="${2:-$(pwd)}"
RETENTION_DAYS="${3:-30}"
BACKUP_MEDIA=false
MEDIA_BACKUP_DIR=""

# Parse optional --media flag
shift 3 2>/dev/null || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --media)
            BACKUP_MEDIA=true
            MEDIA_BACKUP_DIR="${2:-}"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

cd "$PROJECT_PATH"

# --- Database backup ---
log "Starting database backup..."
docker compose -f "$COMPOSE_FILE" exec -T postgres backup

log "Cleaning up database backups older than $RETENTION_DAYS days..."
docker compose -f "$COMPOSE_FILE" exec -T postgres cleanup $RETENTION_DAYS

log "Current database backups:"
docker compose -f "$COMPOSE_FILE" exec -T postgres backups

# --- Media backup ---
if [ "$BACKUP_MEDIA" = true ] && [ -n "$MEDIA_BACKUP_DIR" ]; then
    MEDIA_FILENAME="media_$(date +'%Y_%m_%dT%H_%M_%S').tar.gz"

    log "Starting media backup..."
    docker compose -f "$COMPOSE_FILE" run --rm \
        -v "$MEDIA_BACKUP_DIR:/host-backups" \
        django tar czf "/host-backups/$MEDIA_FILENAME" -C /data media/

    log "Cleaning up media backups older than $RETENTION_DAYS days..."
    find "$MEDIA_BACKUP_DIR" -name "media_*.tar.gz" -mtime +"$RETENTION_DAYS" -delete

    log "Current media backups:"
    ls -lht "$MEDIA_BACKUP_DIR"
fi

log "Backup complete!"
