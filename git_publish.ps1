# Git publish script for Windows PowerShell
# This script will initialize git, commit, and prepare for GitHub push

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Account Plan Agent - Git Publish Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    git --version | Out-Null
} catch {
    Write-Host "Error: Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Git from https://git-scm.com/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Initialize git repository if not already initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing Git repository..." -ForegroundColor Green
    git init
    Write-Host ""
}

# Add all files
Write-Host "Adding files to git..." -ForegroundColor Green
git add .
Write-Host ""

# Create commit with multiline message
Write-Host "Creating commit..." -ForegroundColor Green
$commitMessage = @"
Initial release v1.0.0

- Complete AI-powered account planning system
- Full English documentation
- Multiple installation options for compatibility
- Comprehensive bug fixes and improvements
- Production-ready code
"@

git commit -m $commitMessage
Write-Host ""

# Create tag (delete if exists)
Write-Host "Creating version tag..." -ForegroundColor Green
git tag -d v1.0.0 2>$null
git tag -a v1.0.0 -m "Release v1.0.0"
Write-Host ""

# Prompt for GitHub username
$githubUser = Read-Host "Enter your GitHub username"
Write-Host ""

# Add remote (remove if exists)
Write-Host "Adding GitHub remote..." -ForegroundColor Green
git remote remove origin 2>$null
git remote add origin "https://github.com/$githubUser/account-plan-agent-english.git"
Write-Host ""

# Set main branch
Write-Host "Setting main branch..." -ForegroundColor Green
git branch -M main
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Git repository prepared successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create a new repository on GitHub named: account-plan-agent-english"
Write-Host "2. Then run: .\git_push.ps1"
Write-Host ""
Write-Host "Or manually push with:" -ForegroundColor Yellow
Write-Host "  git push -u origin main"
Write-Host "  git push origin --tags"
Write-Host ""
Read-Host "Press Enter to exit"

