@echo off
setlocal
cd /d "%~dp0"
echo Starting SafePassage local stack...
powershell -ExecutionPolicy Bypass -File "%~dp0infra\dev\stack.ps1" up
echo.
echo ========================================================
echo ReliefRoute is starting up!
echo Web App:    http://localhost:3000
echo API Docs:   http://localhost:8000/docs
echo Logs:       %USERPROFILE%\reliefroute-data\logs
echo ========================================================
echo.
pause

