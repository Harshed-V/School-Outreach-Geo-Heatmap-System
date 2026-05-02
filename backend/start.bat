@echo off
REM Quick startup script for development (Windows)

echo.
echo ============================================================
echo Entering backend directory...
echo ============================================================

cd backend

echo.
echo ============================================================
echo Running diagnostic check...
echo ============================================================

python diagnose.py

echo.
echo ============================================================
echo Starting Backend (Python)...
echo ============================================================
echo.

python app.py
