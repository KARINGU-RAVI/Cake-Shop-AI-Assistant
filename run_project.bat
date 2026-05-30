@echo off
echo ===================================================
echo   Starting The Cake Shop AI Sales Agent...
echo ===================================================
echo.
echo Active Virtual Environment...
call venv\Scripts\activate.bat
echo.
echo Starting FastAPI Web Server...
uvicorn app.main:app --reload
pause
    