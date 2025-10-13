@echo off
REM Git push script for Windows
REM Use this after creating the GitHub repository

echo ==========================================
echo Account Plan Agent - Git Push Script
echo ==========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Error: Git repository not initialized
    echo Please run git_publish.bat first
    pause
    exit /b 1
)

echo Pushing to GitHub...
echo.

REM Push main branch
echo Pushing main branch...
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to push main branch
    echo.
    echo Common issues:
    echo 1. Branch protection rules enabled on GitHub
    echo    - Go to Settings -^> Branches -^> Remove or edit protection rules
    echo 2. GitHub repository not created yet
    echo 3. Authentication failed - you may need a Personal Access Token
    echo 4. Remote URL incorrect
    echo.
    echo Quick Fix for "repository rule violations":
    echo 1. Go to: https://github.com/harry720320/account-plan-agent-english/settings/branches
    echo 2. Remove or edit any branch protection rules for 'main'
    echo 3. Run git_push.bat again
    echo.
    echo See GITHUB_PUSH_TROUBLESHOOTING.md for detailed solutions
    echo.
    pause
    exit /b 1
)
echo.

REM Push tags
echo Pushing tags...
git push origin --tags
if %errorlevel% neq 0 (
    echo.
    echo Warning: Failed to push tags
    pause
    exit /b 1
)
echo.

echo ==========================================
echo Successfully pushed to GitHub!
echo ==========================================
echo.
echo Your repository is now live at:
echo https://github.com/YOUR_USERNAME/account-plan-agent-english
echo.
echo Next steps:
echo 1. Go to your GitHub repository
echo 2. Create a new Release from tag v1.0.0
echo 3. Copy content from RELEASE_NOTES.md as release description
echo.
pause

