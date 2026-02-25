#!/bin/bash
# Server provisioning script
## Execution order:
### 1. Parse script arguments
### 2. Load `../ansible/.env.ansible`
### 3. Build ansible-playbook command with dynamic vars
### 4. Setup GitHub Actions SSH key
### 5. Auto-detect git repository info
### 6. Finish building ansible command
### 7. Execute ansible-playbook


set -e

CLOUD_PROVIDER=${1:-aws}
ENVIRONMENT=${2:-production}
SERVER_IP=${3}
SSH_USER=${4:-}
SSH_KEY_PATH=${5:-}

if [ -z "$SERVER_IP" ]; then
    echo "Usage: $0 <cloud_provider> <environment> <server_ip> [ssh_user]"
    echo "Example: $0 aws production 192.168.0.1 ubuntu ~/.ssh/mykey.pem"
    echo "Example: $0 digitalocean dev 192.168.0.1 root ~/.ssh/mykey.pem"
    exit 1
fi

if [ -n "$SSH_KEY_PATH" ] && [ ! -f "$SSH_KEY_PATH" ]; then
    echo "Error: SSH key file not found: $SSH_KEY_PATH"
    exit 1
fi

echo "=== Server Provisioning ==="
echo "Provider: $CLOUD_PROVIDER | Env: $ENVIRONMENT | IP: $SERVER_IP"
[ -n "$SSH_USER" ] && echo "SSH User: $SSH_USER (override)" || echo "SSH User: from .env.ansible"
[ -n "$SSH_KEY_PATH" ] && echo "SSH Key: $SSH_KEY_PATH (override)" || echo "SSH Key: default"
echo "==========================="

cd "$(dirname "$0")/../ansible" || exit 1

# Clear previous log
> ansible.log

# Load .env.ansible
if [ -f ".env.ansible" ]; then
    echo -e "\n Loading .env.ansible"
    set -a
    source .env.ansible
    set +a
else
    echo -e "\n Error: .env.ansible not found"
    echo "See ansible/.env.ansible.example for template"
    exit 1
fi

# Build ansible pipeline
echo -e "\n Building ansible command..."
ANSIBLE_CMD="ansible-playbook -i $SERVER_IP,"
[ -n "$SSH_KEY_PATH" ] && ANSIBLE_CMD="$ANSIBLE_CMD --private-key='${SSH_KEY_PATH}'"
ANSIBLE_CMD="$ANSIBLE_CMD -e deploy_env=${ENVIRONMENT}"
ANSIBLE_CMD="$ANSIBLE_CMD -e cloud_provider=${CLOUD_PROVIDER}"
ANSIBLE_CMD="$ANSIBLE_CMD -e auto_reboot=false"
ANSIBLE_CMD="$ANSIBLE_CMD -e deploy_app=true"

# Pass critical vars (group_vars don't load with comma-separated inventory)
[ -n "$APP_USER" ] && ANSIBLE_CMD="$ANSIBLE_CMD -e app_user='${APP_USER}'"
[ -n "$ANSIBLE_REMOTE_USER" ] && ANSIBLE_CMD="$ANSIBLE_CMD -e ansible_user='${ANSIBLE_REMOTE_USER}'"
[ -n "$SSH_USER" ] && ANSIBLE_CMD="$ANSIBLE_CMD -e ansible_user='${SSH_USER}'"

# GitHub Actions SSH key setup
echo -e "\n GitHub Actions SSH key"
SSH_KEY_DIR="$HOME/.ssh"
SSH_KEY_FILE="$SSH_KEY_DIR/github_actions"

if [ -z "$GITHUB_ACTIONS_SSH_KEY" ]; then
    if [ -f "$SSH_KEY_FILE.pub" ]; then
        echo "Using existing key: $SSH_KEY_FILE.pub"
        GITHUB_ACTIONS_SSH_KEY=$(cat "$SSH_KEY_FILE.pub" | tr -d '\n' | xargs)
    else
        echo "Generating new key..."
        mkdir -p "$SSH_KEY_DIR"
        ssh-keygen -t ed25519 -C "github-actions" -f "$SSH_KEY_FILE" -N "" -q
        GITHUB_ACTIONS_SSH_KEY=$(cat "$SSH_KEY_FILE.pub" | tr -d '\n' | xargs)
        echo "Generated: $SSH_KEY_FILE"
    fi
    export GITHUB_ACTIONS_SSH_KEY

    echo ""
    echo "  Add private key to GitHub Secrets:"
    echo "  Repository Settings > Secrets > Actions"
    echo "  Secret name: PROD_SSH_KEY"
    echo "  Key location: $SSH_KEY_FILE"
    echo ""
else
    echo "Key loaded from .env.ansible"
    export GITHUB_ACTIONS_SSH_KEY
fi

# Auto-detect git repository
echo -e "\n Git repository configuration"
if [ -z "$GIT_REPO_URL" ] && git remote get-url origin &>/dev/null; then
    ORIGIN_URL=$(git remote get-url origin 2>/dev/null)
    REPO_PATH=""
    GIT_HOST=""
    
    # Parse various Git URL formats to extract repository path and host
    if [[ "$ORIGIN_URL" =~ ^git@([^:]+):(.+)$ ]]; then
        # SSH format: git@github.com:user/repo.git
        GIT_HOST="${BASH_REMATCH[1]}"
        REPO_PATH="${BASH_REMATCH[2]}"
    elif [[ "$ORIGIN_URL" =~ ^https?://([^/]+)/(.+)$ ]]; then
        # HTTPS format: https://github.com/user/repo.git
        # Strip userinfo (user:pass@) if present
        GIT_HOST="${BASH_REMATCH[1]##*@}"
        REPO_PATH="${BASH_REMATCH[2]}"
    elif [[ "$ORIGIN_URL" =~ ^ssh://git@([^/]+)/(.+)$ ]]; then
        # SSH URL format: ssh://git@github.com/user/repo.git
        GIT_HOST="${BASH_REMATCH[1]}"
        REPO_PATH="${BASH_REMATCH[2]}"
    fi
    
    if [ -n "$REPO_PATH" ] && [ -n "$GIT_HOST" ]; then
        # Remove .git suffix if present, then add it back for consistency
        REPO_PATH="${REPO_PATH%.git}"
        # Validate that REPO_PATH has exactly two non-empty components (user/repo)
        if [[ "$REPO_PATH" =~ ^[^/]+/[^/]+$ ]]; then
            DETECTED_URL="git@${GIT_HOST}:${REPO_PATH}.git"
            GIT_REPO_URL="$DETECTED_URL"
        fi
    fi
fi

if [ -z "$GIT_BRANCH" ] && git rev-parse --abbrev-ref HEAD &>/dev/null; then
    GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
fi
GIT_BRANCH=${GIT_BRANCH:-main}

if [ -n "$GIT_REPO_URL" ]; then
    echo "Repo: $GIT_REPO_URL"
    echo "Branch: $GIT_BRANCH"
else
    echo "No GIT_REPO_URL - app deployment will be skipped"
fi

# Pass environment vars to Ansible
echo -e "\nPassing variables to Ansible"
for var in DOMAIN_NAME SSL_EMAIL DB_PASSWORD GIT_REPO_URL GIT_BRANCH PROJECT_NAME; do
    if [ -n "${!var}" ]; then
        ansible_var=$(echo "$var" | tr '[:upper:]' '[:lower:]')
        ANSIBLE_CMD="$ANSIBLE_CMD -e ${ansible_var}='${!var}'"
    else
        echo "$var - not provided. Update ansible/.env.ansible."
        exit 1
    fi
done

ANSIBLE_CMD="$ANSIBLE_CMD playbooks/provision.yml"

# Display masked command
MASKED_CMD=$(echo "$ANSIBLE_CMD" | sed -E "s/(db_password)='[^']*'/\1='***'/g")
echo "$MASKED_CMD"
echo "(GITHUB_ACTIONS_SSH_KEY passed via environment)"

# Execute
echo ""
eval $ANSIBLE_CMD

echo -e "\n=== Provisioning Complete ==="
echo "Next steps:"
echo "1. Review provisioning summary above"
echo "2. Verify app: http://$SERVER_IP"
echo "3. Reboot if required"

if [ "$CLOUD_PROVIDER" = "aws" ]; then
    echo ""
    echo "  AWS Security Groups (manual step):"
    echo "  Open EC2 > Security Groups in the AWS Console"
    echo "  and add inbound rules to your instance's security group:"
    echo "    - SSH (port 22) from 0.0.0.0/0"
    echo "    - HTTP (port 80) from 0.0.0.0/0"
    echo "    - HTTPS (port 443) from 0.0.0.0/0"
fi
echo ""
