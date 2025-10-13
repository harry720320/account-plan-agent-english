# Git push script for Windows PowerShell
# Use this after creating the GitHub repository

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Account Plan Agent - Git Push Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "Error: Git repository not initialized" -ForegroundColor Red
    Write-Host "Please run .\git_publish.ps1 first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Pushing to GitHub..." -ForegroundColor Green
Write-Host ""

# Push main branch
Write-Host "Pushing main branch..." -ForegroundColor Green
try {
    git push -u origin main
    if ($LASTEXITCODE -ne 0) {
        throw "Push failed"
    }
} catch {
    Write-Host ""
    Write-Host "Error: Failed to push main branch" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Branch protection rules enabled on GitHub"
    Write-Host "   - Go to Settings -> Branches -> Remove or edit protection rules"
    Write-Host "2. GitHub repository not created yet"
    Write-Host "3. Authentication failed - you may need a Personal Access Token"
    Write-Host "4. Remote URL incorrect"
    Write-Host ""
    Write-Host "Quick Fix for 'repository rule violations':" -ForegroundColor Cyan
    Write-Host "1. Go to: https://github.com/harry720320/account-plan-agent-english/settings/branches"
    Write-Host "2. Remove or edit any branch protection rules for 'main'"
    Write-Host "3. Run .\git_push.ps1 again"
    Write-Host ""
    Write-Host "See GITHUB_PUSH_TROUBLESHOOTING.md for detailed solutions" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Push tags
Write-Host "Pushing tags..." -ForegroundColor Green
try {
    git push origin --tags
    if ($LASTEXITCODE -ne 0) {
        throw "Push tags failed"
    }
} catch {
    Write-Host ""
    Write-Host "Warning: Failed to push tags" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your repository is now live!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to your GitHub repository"
Write-Host "2. Click on 'Releases' -> 'Create a new release'"
Write-Host "3. Select tag: v1.0.0"
Write-Host "4. Title: Account Plan Agent v1.0.0 - Initial Release"
Write-Host "5. Copy content from RELEASE_NOTES.md as description"
Write-Host "6. Click 'Publish release'"
Write-Host ""
Read-Host "Press Enter to exit"

