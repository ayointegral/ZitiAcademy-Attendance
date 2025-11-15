# CI/CD Quick Start

## 🚀 Get Started in 5 Minutes

### Prerequisites
- GitHub account
- Docker installed locally
- Git installed

### Quick Setup

```bash
# 1. Initialize git (if not done)
git init
git add .
git commit -m "feat: initial commit with CI/CD pipeline"

# 2. Create GitHub repo at https://github.com/new

# 3. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/ZitiAcademy-Attendance.git
git branch -M main
git push -u origin main

# 4. Watch your pipeline run!
# Go to: https://github.com/YOUR_USERNAME/ZitiAcademy-Attendance/actions
```

That's it! Your CI/CD pipeline is now active. 🎉

---

## 📋 What Happens Automatically

### On Every Push
✅ Code linting (Python & TypeScript)  
✅ Security scanning  
✅ Unit tests  
✅ Docker image builds  
✅ Integration tests  
✅ Vulnerability scanning  

### On Push to `develop` branch
✅ All of the above, plus:  
✅ Deploy to staging environment  

### On Push to `main` branch
✅ All of the above, plus:  
✅ Deploy to production environment  
✅ Tag Docker images as `latest`  

---

## 🔧 Essential Commands

```bash
# Test locally before pushing
docker compose up

# Rebuild after code changes
docker compose up --build

# View logs
docker compose logs -f

# Stop services
docker compose down

# Run backend tests
cd backend && python -m pytest

# Run frontend lint
cd frontend && npm run lint
```

---

## 🔑 Required GitHub Secrets

Go to: **Settings → Secrets and variables → Actions**

### Minimum Required
- No secrets required for basic CI/CD!

### For Production Deployment
- `PRODUCTION_HOST` - Your server IP/domain
- `PRODUCTION_USER` - SSH username
- `PRODUCTION_SSH_KEY` - SSH private key
- `API_BASE_URL` - Production API URL

---

## 📊 View Pipeline Status

### Check Current Status
```
https://github.com/YOUR_USERNAME/ZitiAcademy-Attendance/actions
```

### Add Status Badge to README
```markdown
![CI/CD](https://github.com/YOUR_USERNAME/ZitiAcademy-Attendance/workflows/CI%2FCD%20Pipeline/badge.svg)
```

---

## 🎯 Common Workflows

### Create a Feature
```bash
git checkout -b feat/my-feature
# ... make changes ...
git add .
git commit -m "feat: add new feature"
git push origin feat/my-feature
# Create PR on GitHub → CI runs automatically
```

### Deploy to Staging
```bash
git checkout develop
git merge feat/my-feature
git push origin develop
# Automatically deploys to staging
```

### Deploy to Production
```bash
git checkout main
git merge develop
git push origin main
# Automatically deploys to production
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Pipeline fails on lint | Run `npm run lint` or `flake8 app` locally |
| Docker build fails | Run `docker compose build` locally to debug |
| Tests fail | Run `pytest` or `npm test` locally |
| Can't push images | Check GitHub token has `write:packages` permission |
| Deployment fails | Verify secrets are configured correctly |

---

## 📚 Full Documentation

For detailed information, see:
- **[CICD_GUIDE.md](./CICD_GUIDE.md)** - Complete CI/CD documentation
- **[DOCKER_SETUP.md](./DOCKER_SETUP.md)** - Docker configuration
- **[DEPLOYMENT_SUCCESS.md](./DEPLOYMENT_SUCCESS.md)** - Deployment guide

---

## 💡 Pro Tips

1. **Always test locally first**: `docker compose up`
2. **Use conventional commits**: `feat:`, `fix:`, `docs:`, etc.
3. **Keep PRs small**: Easier to review and test
4. **Check CI status before merging**: Green checks = good to go
5. **Monitor production after deployment**: Watch for errors

---

## 🆘 Need Help?

1. Check workflow logs in GitHub Actions
2. Review [CICD_GUIDE.md](./CICD_GUIDE.md)
3. Check [GitHub Actions docs](https://docs.github.com/en/actions)

---

**Ready to deploy?** Just push to GitHub! 🚀
