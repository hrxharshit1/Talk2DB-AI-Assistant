@echo off
cd /d "%~dp0"
echo Stopping old processes...
taskkill /F /IM python.exe >nul 2>&1
echo.
echo Starting Database Query App (Flask)...
echo - URL: http://127.0.0.1:5000
echo.
echo Please wait...
".\venv\Scripts\python.exe" app.py
pause
