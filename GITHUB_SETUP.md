# 🔧 GitHub Actions CI/CD Setup

## Step 1: Generate SSH Key (on Server)

```bash
ssh administrator@81.88.26.204

# Generate new key pair for deployments
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy -N ""

# Add public key to authorized_keys
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys

# Copy private key (you'll need this for GitHub)
cat ~/.ssh/github_deploy
```

## Step 2: Add GitHub Secrets

Go to: **GitHub Repo → Settings → Secrets and Variables → Actions**

Add these secrets:

| Secret Name | Value |
|------------|-------|
| `SSH_PRIVATE_KEY` | Contents of `~/.ssh/github_deploy` (private key) |
| `SAFETY_API_KEY` | (Optional) From https://pyup.io for security scans |

## Step 3: Add Workflow File

Copy `.github/workflows/deploy.yml` to your repository:

```
your-repo/
└── .github/
    └── workflows/
        └── deploy.yml
```

## Step 4: Test Deployment

```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

Check: **GitHub → Actions** tab for deployment status.

## Step 5: Server Preparation

Ensure server has git configured:

```bash
ssh administrator@81.88.26.204

cd /var/www/westmoney
git init  # if not already
git remote add origin https://github.com/YOUR_USERNAME/westmoney.git
git fetch origin
git checkout main

# Create backups directory
mkdir -p backups
```

## Workflow Triggers

| Trigger | Action |
|---------|--------|
| Push to `main` | Auto deploy |
| Push to `master` | Auto deploy |
| Pull Request | Run tests only |
| Manual | Click "Run workflow" in Actions |

## Environment: Production

The deploy job uses `environment: production` which allows:
- Required reviewers
- Wait timer
- Environment-specific secrets

Configure at: **Settings → Environments → New environment → "production"**

---

## Troubleshooting

### SSH Connection Failed
```bash
# On server, check SSH is running
sudo systemctl status ssh

# Verify key permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Permission Denied on Restart
```bash
# Add to /etc/sudoers.d/westmoney
administrator ALL=(ALL) NOPASSWD: /bin/systemctl restart westmoney
administrator ALL=(ALL) NOPASSWD: /bin/systemctl status westmoney
```

### Git Pull Fails
```bash
# Reset any local changes
cd /var/www/westmoney
git fetch origin
git reset --hard origin/main
```
