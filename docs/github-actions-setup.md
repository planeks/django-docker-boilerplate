# GitHub Actions setup for provisioned servers

After provisioning a server with `./scripts/provision-server.sh`, GitHub Actions needs:
1. SSH access to the server
2. The server's IP address
3. Proper directory structure and permissions

The provisioning script configures items 2 and 3 automatically. You need to add the SSH credentials to GitHub.

## Prerequisites

Before provisioning, generate an SSH key pair for GitHub Actions:

```bash
# Generate a new SSH key pair (no passphrase)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions -N ""

# This creates:
# - ~/.ssh/github_actions (private key - for GitHub Secrets)
# - ~/.ssh/github_actions.pub (public key - goes on the server)
```

If you skip this step, `provision-server.sh` will generate the key pair automatically at `~/.ssh/github_actions`.

## Providing the SSH key during provisioning

### Option 1: Let the script handle it

Just run the provisioning script. It auto-generates the key if `~/.ssh/github_actions` doesn't exist:

```bash
./scripts/provision-server.sh aws production 54.123.45.67
```

### Option 2: Set the key explicitly

```bash
export GITHUB_ACTIONS_SSH_KEY=$(cat ~/.ssh/github_actions.pub)
./scripts/provision-server.sh aws production 54.123.45.67
```

### Option 3: Add the key after provisioning

If you forgot to add it during provisioning:

```bash
# SSH to the server
ssh -i <your-key> ubuntu@54.123.45.67

# Add the public key manually
echo "your-public-key-here" >> ~/.ssh/authorized_keys
```

If your app user is different from the SSH user (e.g., `appuser`), also add it there:
```bash
sudo sh -c 'echo "your-public-key-here" >> /home/appuser/.ssh/authorized_keys'
```

## Configure GitHub secrets

After provisioning, add these secrets to your GitHub repository.

Go to: Repository > Settings > Secrets and variables > Actions > New repository secret

### Production

```
PROD_HOST = 54.123.45.67 (your server IP)
PROD_SSH_KEY = (paste entire private key from ~/.ssh/github_actions)
PROD_SSH_USER = ubuntu (optional, defaults to appuser)
```

### Staging

```
STAGING_HOST = your staging server IP
STAGING_SSH_KEY = (private key)
STAGING_SSH_USER = (optional, defaults to appuser)
```

### Development

```
DEV_HOST = your dev server IP
DEV_SSH_KEY = (private key)
DEV_SSH_USER = (optional, defaults to appuser)
```

The private key format looks like:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
...
(entire key content)
...
-----END OPENSSH PRIVATE KEY-----
```

## Verify the setup

Test the SSH connection from your local machine:

```bash
ssh -i ~/.ssh/github_actions ubuntu@54.123.45.67 "echo 'Connection successful'"
```

## Environment file (.env)

After provisioning, a `.env` file is created on the server from the template with generated secrets. Check that the values are set:

```bash
ssh -i <your-key> ubuntu@54.123.45.67
cd ~/projects/django_app
grep -E 'SECRET_KEY|POSTGRES_PASSWORD|ALLOWED_HOSTS' .env
```

If any values are placeholders, update them:
```bash
nano .env
```

Required values:
```bash
SECRET_KEY=your-actual-secret-key-here
POSTGRES_PASSWORD=your-secure-db-password
ALLOWED_HOSTS=yourdomain.com
SITE_DOMAIN=yourdomain.com
SITE_URL=https://yourdomain.com
```

## AWS security groups

You need to manually configure security groups in the AWS Console to allow traffic:

1. Go to EC2 > Security Groups
2. Find your instance's security group
3. Add inbound rules:
   - Type: SSH, Port: 22, Source: 0.0.0.0/0
   - Type: HTTP, Port: 80, Source: 0.0.0.0/0
   - Type: HTTPS, Port: 443, Source: 0.0.0.0/0

## Troubleshooting

### GitHub Actions can't SSH to server

"Permission denied (publickey)" during deployment.

1. Check that the public key is in authorized_keys on the server:
```bash
ssh -i <your-key> ubuntu@54.123.45.67 "cat ~/.ssh/authorized_keys"
```

2. Check that the GitHub Secret has the correct private key:
   - It should start with `-----BEGIN OPENSSH PRIVATE KEY-----`
   - No extra spaces or newlines

3. Test SSH manually:
```bash
ssh -i ~/.ssh/github_actions ubuntu@54.123.45.67
```

4. Check the SSH username. The deploy workflow defaults to `appuser`. If your server uses `ubuntu`, set the `*_SSH_USER` secret (e.g., `PROD_SSH_USER=ubuntu`).

### Port 80/443 not accessible

1. Check the OS firewall:
```bash
ssh -i <your-key> ubuntu@54.123.45.67 "sudo ufw status"
```

2. Check AWS security groups in the console (see section above).

### .env file missing

1. Check if .env exists:
```bash
ssh -i <your-key> ubuntu@54.123.45.67 "ls -la ~/projects/django_app/.env"
```

2. Copy from template:
```bash
ssh -i <your-key> ubuntu@54.123.45.67 "cp ~/projects/django_app/.env.template ~/projects/django_app/.env"
```

3. Edit and fill in actual values.

## Workflows included

```
.github/workflows/
├── ci.yml                 # Runs tests on every push
├── deploy-reusable.yml    # Shared deploy logic
├── dev_deploy.yml         # Deploys on push to develop
├── staging_deploy.yml     # Deploys on push to staging
└── production_deploy.yml  # Deploys on push to main
```

After provisioning and configuring secrets, these workflows run automatically on push to the corresponding branch.

## Security notes

- Use separate SSH keys for each environment (dev/staging/prod) if possible
- Rotate keys at least annually
- Never commit private keys to the repository
- Use GitHub Environments with required reviewers for production
- Restrict security group SSH access to specific IPs if possible (instead of 0.0.0.0/0)

## Setup checklist

- Generate SSH key pair for GitHub Actions (or let `provision-server.sh` generate it)
- Run `./scripts/provision-server.sh`
- Add `*_HOST` to GitHub Secrets
- Add `*_SSH_KEY` to GitHub Secrets
- Add `*_SSH_USER` to GitHub Secrets (if not using `appuser`)
- SSH to server and verify `.env` file has real values
- Test deployment via GitHub Actions
- Verify the site is accessible

---

Related:
- [Manual deployment guide](deployment_manual.md)
- [Automated provisioning guide](deployment_automated.md)
