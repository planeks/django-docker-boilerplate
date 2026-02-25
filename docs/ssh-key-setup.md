# SSH Key Setup for GitHub Actions

This document explains the SSH key setup process for automated deployments.

## Overview

The provisioning process now **automatically handles SSH key creation** and provides clear instructions for adding keys to GitHub.

## Two Types of SSH Keys

### 1. GitHub Actions SSH Key (GitHub → Server)
**Purpose:** Allows GitHub Actions to deploy to your server

- **Location:** `~/.ssh/github_actions` (on your local machine)
- **Direction:** GitHub Actions → Your Server
- **Setup:** Automatic during provisioning

### 2. Deploy Key (Server → GitHub)
**Purpose:** Allows your server to pull code from GitHub

- **Location:** `/home/appuser/.ssh/id_rsa` (on the server)
- **Direction:** Your Server → GitHub Repository
- **Setup:** Automatic during provisioning

## Automatic Setup Process

When you run `ansible-playbook` to provision your server:

### Step 1: SSH Key Check
The playbook checks if `~/.ssh/github_actions` exists on your local machine.

### Step 2: Key Creation (if needed)
If the key doesn't exist, it will:
- Generate an Ed25519 SSH key pair
- Display the **private key** with clear instructions
- Show exactly where to add it in GitHub

### Step 3: Instructions Display
You'll see output like:
```
========================================
✓ GitHub Actions SSH Key Created!
========================================

STEP 1: Add to GitHub Secrets
─────────────────────────────────────────
Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions

Click: "New repository secret"

Add these secrets:

Name:  PROD_HOST
Value: 157.245.67.247

Name:  PROD_SSH_KEY
Value: (copy the PRIVATE KEY below)

┌─────────────────────────────────────────┐
│ PRIVATE KEY - Add to GitHub Secrets    │
└─────────────────────────────────────────┘
-----BEGIN OPENSSH PRIVATE KEY-----
[key content here]
-----END OPENSSH PRIVATE KEY-----
┌─────────────────────────────────────────┐
```

### Step 4: Add to GitHub
1. Copy the private key from the terminal
2. Go to the GitHub URL shown
3. Add `PROD_HOST` with your server IP
4. Add `PROD_SSH_KEY` with the private key content
5. Press ENTER in the terminal to continue

### Step 5: Server Configuration
The playbook automatically:
- Adds the **public key** to the server's `~/.ssh/authorized_keys`
- Configures proper permissions
- Sets up the deployment directory

## Manual Commands

If you need to manage keys manually:

### Generate SSH Key
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions -N ""
```

### View Private Key (for GitHub Secrets)
```bash
cat ~/.ssh/github_actions
```

### View Public Key (for server)
```bash
cat ~/.ssh/github_actions.pub
```

### Export Public Key for Provisioning
```bash
export GITHUB_ACTIONS_SSH_KEY="$(cat ~/.ssh/github_actions.pub)"
ansible-playbook -i inventory/digitalocean.yml playbooks/provision.yml
```

## GitHub Secrets Required

For each environment, you need:

| Environment | Secrets Required |
|-------------|------------------|
| Production | `PROD_HOST`, `PROD_SSH_KEY` |
| Staging | `STAGING_HOST`, `STAGING_SSH_KEY` |
| Development | `DEV_HOST`, `DEV_SSH_KEY` |

**Note:** You can use the same SSH key for all environments by copying the same private key to each secret.

## Security Best Practices

1. ✅ **Never commit private keys** to your repository
2. ✅ **Use different keys** for different repositories (optional but recommended)
3. ✅ **Rotate keys periodically** (e.g., every 6 months)
4. ✅ **Revoke old keys** when no longer needed
5. ✅ **Use read-only deploy keys** when possible (for the server→GitHub key)

## Troubleshooting

### "Permission denied (publickey)" when deploying
- Verify `PROD_SSH_KEY` contains the **entire** private key including header/footer
- Check the public key is in the server's `~/.ssh/authorized_keys`
- Verify the server user matches the deployment workflow

### Key already exists
If `~/.ssh/github_actions` already exists:
- The playbook will use the existing key
- You'll see a reminder to verify it's added to GitHub Secrets
- Run `cat ~/.ssh/github_actions` to view the private key if needed

### Want to regenerate keys
```bash
rm ~/.ssh/github_actions ~/.ssh/github_actions.pub
ansible-playbook -i inventory/... playbooks/provision.yml
```

## Related Documentation

- [GitHub Actions Setup](github-actions-setup.md)
- [Deployment Guide](deployment.md)
- [Ansible Configuration](../ansible/README.md)
