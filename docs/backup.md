## Backups

### Automated backups (provisioned servers)

If you provisioned the server with Ansible, a weekly cron job is already set up. It runs `scripts/backup.sh` which:
- Creates a database dump inside the postgres container
- Cleans up backups older than 28 days

The backup role configures this automatically for production environments.

### Manual backup

Run the backup script directly on the server:

```bash
cd ~/projects/django_app
./scripts/backup.sh compose.prod.yml ~/projects/django_app
```

Or via SSH:

```bash
ssh -i <your-key> <user>@<server_ip> "cd ~/projects/django_app && ./scripts/backup.sh"
```

### Listing backups

```bash
docker compose -f compose.prod.yml exec -T postgres backups
```

### Media backups

Media backup is disabled by default. There are two ways to enable it:

**Before provisioning** -- set in your Ansible inventory:

```yaml
backup_media_enabled: true
```

**After provisioning** -- create the directory and edit the crontab on the server:

```bash
mkdir -p ~/backups/media
crontab -e
```

Append `--media ~/backups/media` to the existing backup command:

```
0 2 * * 0 /home/ubuntu/backup.sh compose.prod.yml /home/ubuntu/projects/django_app 30 --media /home/ubuntu/backups/media >> /home/ubuntu/backup.log 2>&1
```

When enabled, the weekly cron job will also:

- Create a compressed archive of `/data/media/` from the django container
- Store it at `~/backups/media/media_<timestamp>.tar.gz` on the host
- Clean up media archives older than `backup_retention_days`

#### Manual media backup

```bash
cd ~/projects/django_app
docker compose -f compose.prod.yml run --rm \
  -v ~/backups/media:/host-backups \
  django tar czf /host-backups/media_$(date +'%Y_%m_%dT%H_%M_%S').tar.gz -C /data media/
```

#### Restore media from backup

```bash
docker compose -f compose.prod.yml run --rm \
  -v ~/backups/media:/host-backups \
  django tar xzf /host-backups/media_2026_02_24T02_00_00.tar.gz -C /data
```

## Restore from backup

Stop the app containers that use the database:

```bash
docker compose -f compose.prod.yml stop django celeryworker
```

Restore the database from a specific dump:

```bash
docker compose -f compose.prod.yml exec -T postgres restore <dump_name>
```

Start the containers again:

```bash
docker compose -f compose.prod.yml up -d django celeryworker
```

## Cleaning Docker data

Optionally set up a cron job to prune unused Docker data:

```bash
sudo crontab -e
```

Add:

```bash
0 2 * * *       docker system prune -f >> /home/appuser/docker_prune.log 2>&1
```
