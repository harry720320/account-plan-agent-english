# How to Publish to GitHub - Windows Guide

## 🚀 Quick Start (Recommended)

### Option 1: Using Batch Scripts (Easiest)

**Step 1: Prepare Git Repository**
```cmd
git_publish.bat
```
This will:
- Initialize git repository
- Add all files
- Create initial commit
- Create version tag (v1.0.0)
- Add GitHub remote

**Step 2: Create GitHub Repository**
1. Go to https://github.com/new
2. Repository name: `account-plan-agent-english`
3. Description: `AI-powered customer account planning system`
4. Public repository
5. **Do NOT** initialize with README (we already have one)
6. Click "Create repository"

**Step 3: Push to GitHub**
```cmd
git_push.bat
```

### Option 2: Using PowerShell Scripts

**Step 1: Prepare Git Repository**
```powershell
.\git_publish.ps1
```

**Step 2: Create GitHub Repository** (same as above)

**Step 3: Push to GitHub**
```powershell
.\git_push.ps1
```

---

## 📝 Manual Commands (Alternative)

If you prefer to run commands manually:

### Initialize and Commit
```powershell
# Initialize git
git init

# Add all files
git add .

# Create commit (PowerShell multi-line)
git commit -m "Initial release v1.0.0" `
  -m "" `
  -m "- Complete AI-powered account planning system" `
  -m "- Full English documentation" `
  -m "- Multiple installation options for compatibility" `
  -m "- Comprehensive bug fixes and improvements" `
  -m "- Production-ready code"

# Create tag
git tag -a v1.0.0 -m "Release v1.0.0"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/account-plan-agent-english.git

# Set main branch
git branch -M main
```

### Push to GitHub
```powershell
# Push main branch
git push -u origin main

# Push tags
git push origin --tags
```

---

## 🔐 GitHub Authentication

### Using Personal Access Token (Recommended)

If you get authentication errors:

1. Go to GitHub Settings
2. Developer settings → Personal access tokens → Tokens (classic)
3. Generate new token
4. Select scope: `repo` (Full control of private repositories)
5. Generate token and copy it
6. When git prompts for password, use the token instead

### Using GitHub CLI (Alternative)
```powershell
# Install GitHub CLI
winget install GitHub.cli

# Authenticate
gh auth login

# Then use the scripts above
```

---

## 📋 After Publishing

### Create GitHub Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Choose tag: `v1.0.0`
4. Release title: `Account Plan Agent v1.0.0 - Initial Release`
5. Description: Copy content from `RELEASE_NOTES.md`
6. Click "Publish release"

### Add Repository Information

1. **Description**: AI-powered customer account planning system with intelligent data collection and strategic plan generation
2. **Website**: (if you have one)
3. **Topics**: 
   - ai
   - fastapi
   - streamlit
   - account-planning
   - customer-management
   - openai
   - python
   - strategic-planning
   - crm

---

## ❗ Troubleshooting

### Problem: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/account-plan-agent-english.git
```

### Problem: Authentication failed
- Use Personal Access Token instead of password
- Make sure token has `repo` scope
- Check if username is correct

### Problem: "Updates were rejected"
```powershell
# This means the remote has changes you don't have
# If this is initial push, you can force push
git push -u origin main --force
```

### Problem: PowerShell script won't run
```powershell
# Enable script execution (run PowerShell as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📊 What Gets Published

### Included Files
- ✅ All Python source code (17 files)
- ✅ All documentation (13 files)
- ✅ All configuration files
- ✅ Quick start scripts
- ✅ License (MIT)

### Excluded Files (via .gitignore)
- ❌ `__pycache__/` directories
- ❌ `*.db` database files
- ❌ `.env` environment file
- ❌ `test_*.py` test files
- ❌ `fix_*.py` temporary scripts
- ❌ IDE configuration files

---

## 🎯 Quick Reference

| Task | Batch Script | PowerShell Script | Manual |
|------|-------------|-------------------|---------|
| Prepare Git | `git_publish.bat` | `.\git_publish.ps1` | See manual commands |
| Push to GitHub | `git_push.bat` | `.\git_push.ps1` | `git push -u origin main` |
| View status | `git status` | `git status` | `git status` |
| View log | `git log` | `git log` | `git log` |

---

## ✅ Success Checklist

After publishing, verify:

- [ ] Repository visible on GitHub
- [ ] All files are present
- [ ] README displays correctly
- [ ] License is shown
- [ ] Topics are added
- [ ] Release v1.0.0 is created
- [ ] Repository description is set

---

**You're all set!** 🎉

Your Account Plan Agent is now live on GitHub and ready to be shared with the world!

