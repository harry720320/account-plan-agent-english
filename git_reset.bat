@echo off
REM Git reset script - Use this to start fresh
REM This will remove all git history and start over

echo ==========================================
echo Account Plan Agent - Git Reset Script
echo ==========================================
echo.
echo WARNING: This will delete all git history!
echo You will start with a fresh git repository.
echo.
set /p CONFIRM="Are you sure you want to continue? (yes/no): "

if /i not "%CONFIRM%"=="yes" (
    echo.
    echo Reset cancelled.
    pause
    exit /b 0
)

echo.
echo Removing .git directory...
if exist .git (
    rmdir /s /q .git
    echo Git directory removed.
) else (
    echo No .git directory found.
)

echo.
echo Repository reset complete!
echo.
echo You can now run git_publish.bat to start fresh.
echo.
pause

