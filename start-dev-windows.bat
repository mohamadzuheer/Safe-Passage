@echo off
setlocal
cd /d "%~dp0"

echo Ensuring Docker containers (PostGIS + Redis) are running...
powershell -ExecutionPolicy Bypass -File "%~dp0infra\dev\stack.ps1" ensure-docker
docker compose up -d db redis

echo Running migrations...
cd backend
call "%USERPROFILE%\reliefroute-venv\Scripts\python.exe" -m app.core.migrate
cd ..

echo Starting individual services in dedicated windows...
start "SafePassage - API Server (8000)" cmd /k "cd /d %~dp0backend && %USERPROFILE%\reliefroute-venv\Scripts\python.exe -u -m uvicorn app.main:app --port 8000 --reload"
start "SafePassage - Ingestion Worker" cmd /k "cd /d %~dp0backend && %USERPROFILE%\reliefroute-venv\Scripts\python.exe -u -m app.ingestion.worker"
start "SafePassage - Brain Worker" cmd /k "cd /d %~dp0backend && %USERPROFILE%\reliefroute-venv\Scripts\python.exe -u -m app.graph.worker"
start "SafePassage - Frontend (3000)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================================
echo ReliefRoute local dev stack is running!
echo Web App:    http://localhost:3000
echo API Docs:   http://localhost:8000/docs
echo ========================================================
echo.

