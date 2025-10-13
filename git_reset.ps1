# Git reset script - Use this to start fresh
# This will remove all git history and start over

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Account Plan Agent - Git Reset Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "WARNING: This will delete all git history!" -ForegroundColor Red
Write-Host "You will start with a fresh git repository." -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Are you sure you want to continue? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host ""
    Write-Host "Reset cancelled." -ForegroundColor Green
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "Removing .git directory..." -ForegroundColor Yellow

if (Test-Path .git) {
    Remove-Item -Path .git -Recurse -Force
    Write-Host "Git directory removed." -ForegroundColor Green
} else {
    Write-Host "No .git directory found." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Repository reset complete!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run .\git_publish.ps1 to start fresh." -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"

