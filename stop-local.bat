@echo off
setlocal
cd /d "%~dp0"
echo Stopping SafePassage local stack...
powershell -ExecutionPolicy Bypass -File "%~dp0infra\dev\stack.ps1" down
echo Stopped.
pause

