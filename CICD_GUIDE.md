# CI/CD Pipeline Guide

## 📋 Overview

This project uses GitHub Actions for continuous integration and deployment. The pipeline automatically tests, builds, and deploys your application when code is pushed to the repository.

## 🔄 Workflow Files

### 1. `ci-cd.yml` - Main Pipeline
**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual dispatch

**Jobs:**
1. **backend-ci**: Tests and validates backend code
2. **frontend-ci**: Tests and validates frontend code
3. **docker-build**: Builds and pushes Docker images to GitHub Container Registry
4. **integration-tests**: Runs full-stack integration tests
5. **security-scan**: Scans for vulnerabilities
6. **deploy-staging**: Deploys to staging environment (develop branch)
7. **deploy-production**: Deploys to production (main branch)

### 2. `pr-check.yml` - Pull Request Validation
**Triggers:**
- Pull request opened, synchronized, or reopened

**Jobs:**
1. **pr-validation**: Validates PR title, checks for conflicts
2. **code-quality**: Checks code quality issues
3. **dependency-check**: Audits dependencies for security issues

## 🚀 Setup Instructions

### Step 1: Initialize Git Repository (if not done)
```bash
cd /Users/ajayifam/Documents/ZitiAcademy/Attendance
git init
git add .
git commit -m "Initial commit with CI/CD pipeline"
```

### Step 2: Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository named `ZitiAcademy-Attendance` (or your preferred name)
3. **DO NOT** initialize with README, .gitignore, or license

### Step 3: Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/ZitiAcademy-Attendance.git
git branch -M main
git push -u origin main
```

### Step 4: Configure GitHub Secrets
Go to your repository settings → Secrets and variables → Actions

Add the following secrets:

#### Required Secrets
- `API_BASE_URL`: Your production API URL (e.g., `https://api.attendance.example.com/api`)

#### Optional Secrets (for deployment)
- `PRODUCTION_HOST`: Production server SSH host
- `PRODUCTION_USER`: SSH username
- `PRODUCTION_SSH_KEY`: Private SSH key for deployment
- `STAGING_HOST`: Staging server SSH host
- `STAGING_USER`: Staging SSH username
- `STAGING_SSH_KEY`: Staging SSH key
- `SLACK_WEBHOOK`: Slack notification webhook URL
- `DISCORD_WEBHOOK`: Discord notification webhook URL

### Step 5: Enable GitHub Actions
1. Go to repository Settings → Actions → General
2. Set workflow permissions to "Read and write permissions"
3. Allow GitHub Actions to create and approve pull requests

### Step 6: Enable GitHub Container Registry
1. Go to your profile Settings → Developer settings → Personal access tokens
2. Create a token with `write:packages` permission
3. The pipeline will automatically push images to `ghcr.io/YOUR_USERNAME/repository`

## 📊 Pipeline Workflow

### For Pull Requests
```
PR Created/Updated
    ↓
PR Validation (title, conflicts, size)
    ↓
Backend CI (lint, test)
    ↓
Frontend CI (lint, type-check, build)
    ↓
Code Quality Checks
    ↓
Dependency Audit
    ↓
✅ All Checks Pass → Ready to Merge
```

### For Push to develop branch
```
Push to develop
    ↓
Backend CI + Frontend CI
    ↓
Build & Push Docker Images
    ↓
Integration Tests
    ↓
Security Scanning
    ↓
Deploy to Staging
    ↓
✅ Staging Updated
```

### For Push to main branch
```
Push to main
    ↓
Backend CI + Frontend CI
    ↓
Build & Push Docker Images (tagged as latest)
    ↓
Integration Tests
    ↓
Security Scanning
    ↓
Deploy to Production
    ↓
Send Notifications
    ↓
✅ Production Updated
```

## 🧪 Integration Tests

The pipeline runs comprehensive integration tests:

### Backend API Tests
- ✅ Health endpoint (`/api/health`)
- ✅ Authentication (`/api/auth/login`)
- ✅ Courses endpoint (`/api/courses`)
- ✅ Users endpoint (`/api/users`)
- ✅ CORS configuration
- ✅ JWT token generation

### Frontend Tests
- ✅ Homepage accessibility
- ✅ Login page rendering
- ✅ Static asset serving

### Full-Stack Tests
- ✅ Frontend-to-backend communication
- ✅ CORS headers
- ✅ Cookie management
- ✅ Protected route access

## 🐳 Docker Images

Images are automatically built and pushed to GitHub Container Registry:

### Backend Image
```
ghcr.io/YOUR_USERNAME/zitiacademy-attendance/backend:latest
ghcr.io/YOUR_USERNAME/zitiacademy-attendance/backend:main-abc1234
ghcr.io/YOUR_USERNAME/zitiacademy-attendance/backend:develop
```

### Frontend Image
```
ghcr.io/YOUR_USERNAME/zitiacademy-attendance/frontend:latest
ghcr.io/YOUR_USERNAME/zitiacademy-attendance/frontend:main-abc1234
ghcr.io/YOUR_USERNAME/zitiacademy-attendance/frontend:develop
```

### Pull Images
```bash
# Authenticate
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Pull backend
docker pull ghcr.io/YOUR_USERNAME/zitiacademy-attendance/backend:latest

# Pull frontend
docker pull ghcr.io/YOUR_USERNAME/zitiacademy-attendance/frontend:latest
```

## 🔒 Security Scanning

### Trivy Scanner
Scans for:
- OS package vulnerabilities
- Language-specific vulnerabilities (Python, Node.js)
- Configuration issues
- Secrets in code

Results are uploaded to GitHub Security tab.

### Dependency Audits
- **Backend**: `safety check` for Python packages
- **Frontend**: `npm audit` for Node.js packages

## 📝 Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding tests
- `chore`: Build/tooling changes
- `ci`: CI/CD changes

### Examples
```
feat: add QR code scanner for student check-in
fix(backend): resolve CORS issue on login endpoint
docs: update deployment guide
ci: add security scanning to pipeline
```

## 🏗️ Deployment Setup

### Option 1: Deploy to VPS/Cloud Server

Create a deployment script:

```bash
# deploy.sh
#!/bin/bash
set -e

HOST=$1
USER=$2
SSH_KEY=$3

# Copy docker-compose to server
scp -i $SSH_KEY docker-compose.yml $USER@$HOST:~/attendance/

# Deploy on server
ssh -i $SSH_KEY $USER@$HOST << 'EOF'
  cd ~/attendance
  
  # Login to GitHub Container Registry
  echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USER --password-stdin
  
  # Pull latest images
  docker compose pull
  
  # Start services
  docker compose up -d
  
  # Run migrations/seed if needed
  docker compose exec -T backend python seed.py
  
  # Health check
  sleep 10
  curl -f http://localhost:5001/api/health || exit 1
  
  echo "✅ Deployment successful!"
EOF
```

Update `deploy-production` job in `ci-cd.yml`:
```yaml
- name: Deploy to production
  env:
    HOST: ${{ secrets.PRODUCTION_HOST }}
    USER: ${{ secrets.PRODUCTION_USER }}
    SSH_KEY: ${{ secrets.PRODUCTION_SSH_KEY }}
  run: |
    echo "$SSH_KEY" > deploy_key
    chmod 600 deploy_key
    ./deploy.sh $HOST $USER deploy_key
```

### Option 2: Deploy to Heroku

Add to workflow:
```yaml
- name: Deploy to Heroku
  uses: akhileshns/heroku-deploy@v3.13.15
  with:
    heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
    heroku_app_name: "attendance-app"
    heroku_email: "your-email@example.com"
```

### Option 3: Deploy to AWS ECS

Use AWS Actions:
```yaml
- name: Deploy to Amazon ECS
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
  with:
    task-definition: task-definition.json
    service: attendance-service
    cluster: attendance-cluster
```

## 📈 Monitoring & Notifications

### Add Slack Notifications

Add to your workflow:
```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: |
      Deployment ${{ job.status }}
      Commit: ${{ github.event.head_commit.message }}
      Author: ${{ github.actor }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Add Discord Notifications

```yaml
- name: Notify Discord
  if: always()
  uses: sarisia/actions-status-discord@v1
  with:
    webhook: ${{ secrets.DISCORD_WEBHOOK }}
    status: ${{ job.status }}
    title: "Deployment Status"
    description: "Build #${{ github.run_number }}"
```

## 🔍 Viewing Pipeline Results

### On GitHub
1. Go to your repository
2. Click "Actions" tab
3. See all workflow runs
4. Click on a run to see details
5. Check logs for each job

### Status Badge
Add to your README.md:
```markdown
![CI/CD Pipeline](https://github.com/YOUR_USERNAME/ZitiAcademy-Attendance/workflows/CI%2FCD%20Pipeline/badge.svg)
```

## 🐛 Troubleshooting

### Pipeline Fails on Backend CI
- Check Python version compatibility
- Verify requirements.txt is correct
- Check for syntax errors in Python code

### Pipeline Fails on Frontend CI
- Check Node.js version
- Run `npm install` locally to verify
- Fix TypeScript errors
- Fix linting issues

### Docker Build Fails
- Check Dockerfile syntax
- Verify all files are in context
- Check for missing dependencies

### Integration Tests Fail
- Check if services start correctly
- Verify health checks
- Check logs: `docker compose logs`

### Deployment Fails
- Verify secrets are set correctly
- Check SSH key permissions
- Verify server access
- Check firewall rules

## 📚 Best Practices

### Before Pushing Code
```bash
# Run tests locally
cd backend && python -m pytest
cd frontend && npm test

# Check linting
cd backend && flake8 app
cd frontend && npm run lint

# Build locally
docker compose build

# Test locally
docker compose up
```

### Creating Pull Requests
1. Create a feature branch: `git checkout -b feat/my-feature`
2. Make changes and commit with conventional commit messages
3. Push to GitHub: `git push origin feat/my-feature`
4. Create PR with descriptive title
5. Wait for CI checks to pass
6. Request review
7. Merge after approval

### Merging to Production
1. Merge PR to `develop` first
2. Test in staging environment
3. Create release PR from `develop` to `main`
4. Merge to trigger production deployment
5. Monitor production after deployment

## 📞 Support

If you encounter issues with the CI/CD pipeline:

1. Check workflow logs in GitHub Actions
2. Review this documentation
3. Check GitHub Actions documentation
4. Review Docker documentation for container issues

## 🎯 Next Steps

1. ✅ **Set up GitHub repository**
2. ✅ **Configure secrets**
3. ✅ **Push code to GitHub**
4. ✅ **Verify pipeline runs**
5. ⚪ **Set up staging environment**
6. ⚪ **Set up production environment**
7. ⚪ **Configure deployment scripts**
8. ⚪ **Add monitoring & alerts**
9. ⚪ **Document runbooks**
10. ⚪ **Set up backup strategy**

---

**Created:** 2025-11-15  
**Last Updated:** 2025-11-15  
**Pipeline Version:** 1.0
