@echo off
REM Git publish script for Windows
REM This script will initialize git, commit, and prepare for GitHub push

echo ==========================================
echo Account Plan Agent - Git Publish Script
echo ==========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

REM Initialize git repository if not already initialized
if not exist .git (
    echo Initializing Git repository...
    git init
    echo.
)

REM Add all files
echo Adding files to git...
git add .
echo.

REM Create commit
echo Creating commit...
git commit -m "Initial release v1.0.0" -m "" -m "- Complete AI-powered account planning system" -m "- Full English documentation" -m "- Multiple installation options for compatibility" -m "- Comprehensive bug fixes and improvements" -m "- Production-ready code"
echo.

REM Create tag (delete if exists)
echo Creating version tag...
git tag -d v1.0.0 >nul 2>&1
git tag -a v1.0.0 -m "Release v1.0.0"
echo.

REM Prompt for GitHub username
set /p GITHUB_USER="Enter your GitHub username: "
echo.

REM Add remote (remove if exists)
echo Adding GitHub remote...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/%GITHUB_USER%/account-plan-agent-english.git
echo.

REM Set main branch
echo Setting main branch...
git branch -M main
echo.

echo ==========================================
echo Git repository prepared successfully!
echo ==========================================
echo.
echo Next steps:
echo 1. Create a new repository on GitHub named: account-plan-agent-english
echo 2. Then run: git_push.bat
echo.
echo Or manually push with:
echo   git push -u origin main
echo   git push origin --tags
echo.
pause

