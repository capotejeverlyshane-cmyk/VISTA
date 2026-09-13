@echo off
color 0B
echo =======================================================
echo          STARTING VISTA SYSTEM (DEFENSE MODE)
echo =======================================================
echo.
echo [1/2] Starting Frontend Web Server...
start "VISTA Frontend (Port 8085)" cmd /k "cd frontend && echo Starting server... && npx -y http-server . -p 8085 --cors -c-1"

echo [2/2] Starting Python Backend Server...
start "VISTA Backend (Port 8000)" cmd /k "cd backend && echo Activating Virtual Environment... && (if exist .venv\Scripts\activate (call .venv\Scripts\activate) else if exist venv\Scripts\activate (call venv\Scripts\activate)) && echo Starting FastAPI Server... && uvicorn app:app --reload --port 8000"

echo.
echo -------------------------------------------------------
echo SYSTEM IS RUNNING
echo -------------------------------------------------------
echo Citizen Portal: http://127.0.0.1:8085/index.html
echo Admin Dashboard:  http://127.0.0.1:8085/admin.html
echo Backend API:      http://127.0.0.1:8000
echo.
echo Note: Keep the two black command prompt windows open.
echo Closing them will shut down the system.
echo -------------------------------------------------------
echo.
pause
