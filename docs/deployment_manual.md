## Deploying the project to the server

Modify this section according to the project needs.

### Configure main user

Deploy the project with an unprivileged user instead of `root`.

> On AWS EC2, you already have an unprivileged user called `ubuntu` by default. If that user exists, you don't need to create another one.

You can create a user (for example `appuser`) with:

```shell
$ adduser appuser
```

You will be asked for a password. You can use [https://www.random.org/passwords/](https://www.random.org/passwords/) to generate one.

Add the new user to the `sudo` group:

```bash
$ usermod -aG sudo appuser
```

Set up SSH key authentication. If you don't have a key yet, create one on your local machine:

```bash
$ ssh-keygen -t rsa
```

> This works on Linux and Mac OS. On Windows, use PuTTYgen.

Get your public key:

```bash
$ cat ~/.ssh/id_rsa.pub
```

On the server, switch to the new user:

```bash
$ su - appuser
```

Create the `.ssh` directory and set permissions:

```bash
$ mkdir ~/.ssh
$ chmod 700 ~/.ssh
```

Open `authorized_keys` in a text editor:

```bash
$ nano ~/.ssh/authorized_keys
```

> If `nano` is not installed, use `vi`. Press `i` to enter insert mode, paste your key, then press `Esc` followed by `:wq` to save and exit. Use `:q!` to exit without saving.

Paste your public key into the file, save, and close.

Set permissions on the file:

```bash
$ chmod 600 ~/.ssh/authorized_keys
```

Return to root:

```bash
$ exit
```

Log out of the server and test key-based login:

```bash
$ ssh appuser@XXX.XXX.XXX.XXX
```

If you added the public key correctly, it will authenticate without a password.

To run commands with root privileges:

```bash
$ sudo command_to_run
```

### Install dependencies

Install required packages:

```bash
$ sudo apt install -y git wget tmux htop mc nano build-essential
```

Install Docker and Docker Compose (see Docker's official docs).

Add your user to the docker group:

```bash
$ sudo usermod -aG docker "$USER"
```

Create the `django` group with GID 1024. This is used for non-root volume permissions.

```bash
$ sudo addgroup --gid 1024 django
```

> If GID 1024 is unavailable, pick a different value and update the `Dockerfile` to match.

Add your user to the group:

```bash
$ sudo usermod -aG django ${USER}
$ newgrp django
```

### Generate deploy key

Create an SSH key on the server for pulling code from the remote repository:

    $ ssh-keygen -t rsa

Show the public key:

    $ cat ~/.ssh/id_rsa.pub

Add this key to your repository's deploy keys (on GitHub: Settings > Deploy keys).

> Deploy keys grant read-only access to the repository and don't count against your user quota.

### Clone the project

Create the directory and clone:

```bash
$ mkdir ~/projects
$ cd ~/projects
$ git clone <git_remote_url>
```

Use your actual git remote URL.

Go into the project directory and create initial volumes:

```bash
$ source ./scripts/init_production_volumes.sh
```

Create the `.env` file from the production template:

```shell
$ cp prod.env .env
```

Open `.env` and fill in the values:

```shell
PYTHONENCODING=utf8
COMPOSE_IMAGES_PREFIX=newprojectname
DEBUG=0
CONFIGURATION=prod
DJANGO_LOG_LEVEL=INFO
SECRET_KEY="<secret_key>"
ALLOWED_HOSTS=example.com
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=db
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=<db_password>
REDIS_URL=redis://redis:6379/0
SITE_DOMAIN=example.com
SITE_URL=https://example.com
EMAIL_HOST=
EMAIL_PORT=25
EMAIL_HOST_USER=<email_user>
EMAIL_HOST_PASSWORD=<email_password>
SENTRY_DSN=<sentry_dsn>
CELERY_FLOWER_USER=flower
CELERY_FLOWER_PASSWORD=<flower_password>
CADDY_PASSWORD=<here should be hash of a password>
```

> Generate strong values for `SECRET_KEY` and all passwords.

Set `ALLOWED_HOSTS` and `SITE_DOMAIN` to your actual domain. `COMPOSE_IMAGES_PREFIX` is a prefix for container images and can match your dev configuration.

Build and start:

```bash
$ docker compose -f compose.prod.yml build
$ docker compose -f compose.prod.yml up -d
```

# GitHub Actions setup

## Workflow files

The project already contains these workflows:

```
.github/workflows/
├── ci.yml                    # CI tests for backend and frontend
├── deploy-reusable.yml       # Reusable deployment workflow
├── dev_deploy.yml            # Development deployment
├── staging_deploy.yml        # Staging deployment
└── production_deploy.yml     # Production deployment
```

## Set up environments

In your GitHub repository:

1. Go to Settings > Environments
2. Create three environments:
   - `dev`
   - `staging`
   - `production`

### Production environment protection

For the `production` environment:
1. Click on `production`
2. Enable "Required reviewers"
3. Add team members who should approve production deployments
4. Optionally set a wait timer (e.g., 5 minutes) before deployment

## Configure secrets

For each environment, add the required secrets.

### Development (`dev`)

Go to Settings > Environments > dev > Secrets

- `DEV_HOST` - development server IP or hostname
- `DEV_SSH_KEY` - SSH private key for accessing the dev server
- `DEV_SSH_USER` (optional) - SSH username, defaults to `appuser`

### Staging (`staging`)

Go to Settings > Environments > staging > Secrets

- `STAGING_HOST` - staging server IP or hostname
- `STAGING_SSH_KEY` - SSH private key for accessing the staging server
- `STAGING_SSH_USER` (optional) - SSH username, defaults to `appuser`

### Production (`production`)

Go to Settings > Environments > production > Secrets

- `PROD_HOST` - production server IP or hostname
- `PROD_SSH_KEY` - SSH private key for accessing the production server
- `PROD_SSH_USER` (optional) - SSH username, defaults to `appuser`

### Generating SSH keys

Make sure to not use a passphrase for the key.

```bash
# Generate a new SSH key pair
ssh-keygen -t ed25519 -C "github-actions" -f github_actions_key

# Copy the public key to your server
ssh-copy-id -i github_actions_key.pub appuser@your-server

# Copy the private key content to GitHub Secrets
cat github_actions_key
```

## Set up your servers

Each server (dev, staging, production) needs:

- Docker and Docker Compose installed
- Git installed
- A deploy user created with sudo privileges
- The steps above in this document completed

## How deployments work

### Development

Trigger: push to `develop` branch

1. Deploys to dev server using `compose.dev.yml`
2. Runs database migrations

```bash
git push origin develop
```

Or use Actions > Deploy to Development > Run workflow

### Staging

Trigger: push to `staging` branch

1. Runs CI tests (backend and frontend)
2. Deploys to staging server using `compose.prod.yml`
3. Runs database migrations and collects static files

```bash
git push origin staging
```

Or use Actions > Deploy to Staging > Run workflow

### Production

Trigger: push to `main` branch

1. Runs CI tests (backend and frontend)
2. Requires environment approval
3. Deploys to production server using `compose.prod.yml`
4. Runs database migrations and collects static files

```bash
git push origin main
```

Or use Actions > Deploy to Production > Run workflow

## Branch strategy

```
develop  → Development environment
   ↓
staging  → Staging environment (merge develop here)
   ↓
 main    → Production environment (merge staging here)
```

## Monitoring deployments

### Server health check

Run the health check script on the server to check Docker, disk, memory, load, container health, ports, and firewall:

```bash
ssh -i <your-key> <user>@<server_ip> "bash ~/projects/django_app/scripts/health-check.sh"
```

### View workflow runs

1. Go to the Actions tab in your repository
2. Select a workflow from the left sidebar
3. Click on a specific run to see details

### Troubleshooting

#### Django container fails to start

Symptoms:
- Deployment script reports: `[ERROR] Some services failed to start: django_app-django-run-*`
- Django container exits immediately after starting

Common causes:

1. **Missing or invalid `.env` file**

   The deployment script validates the `.env` file before deploying. If you see:
   ```
   [ERROR] .env file not found!
   [ERROR] SECRET_KEY is not configured in .env file!
   [ERROR] POSTGRES_PASSWORD is not configured in .env file!
   ```

   Fix:
   - Make sure the `.env` file exists on the server
   - Copy from template: `cp prod.env .env` or `cp dev.env .env`
   - Fill in all required values (see below)

2. **Placeholder values in .env**

   The `.env` file must not contain placeholder values like `<secret_key>` or empty values for required fields.

   Required values:
   - `SECRET_KEY` - generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
   - `POSTGRES_PASSWORD` - a secure database password
   - `ALLOWED_HOSTS` - your actual domain (not `example.com`)

   Example fix:
   ```bash
   # SSH into the server
   ssh appuser@your-server

   # Navigate to project directory
   cd ~/projects/django_app

   # Edit .env file
   nano .env

   # Update these values:
   # SECRET_KEY=your-generated-secret-key-here
   # POSTGRES_PASSWORD=your-secure-password-here
   # ALLOWED_HOSTS=yourdomain.com

   # Save and retry deployment
   ./scripts/deploy.sh compose.dev.yml main ~/projects/django_app
   ```

#### General deployment failures

If a deployment fails:
1. Check the workflow logs in the Actions tab
2. SSH into the server and check container logs:
   ```bash
   cd ~/projects/django_app
   docker compose -f compose.prod.yml logs django
   docker compose -f compose.prod.yml ps -a
   ```
3. Verify secrets are correctly set in GitHub
4. Check that the server has proper permissions and resources
5. Check that all required environment variables are set in `.env`

## Security best practices

- Never commit secrets or SSH keys to the repository
- Use environment-specific secrets
- Rotate SSH keys regularly
- Enable branch protection rules for `main` and `staging`
- Require pull request reviews before merging
- Use required reviewers for production deployments

For reference:
- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Docker Compose documentation](https://docs.docker.com/compose/)
