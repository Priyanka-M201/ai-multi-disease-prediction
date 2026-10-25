@echo off
title Disease Prediction System Launcher
echo ========================================================
echo   AI Multi-Disease Risk Prediction & Explainable AI
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/2] Starting Machine Learning Microservice (FastAPI on Port 8000)...
start "ML Service (FastAPI - Port 8000)" cmd /k "cd ml-service && venv\Scripts\python run.py"

timeout /t 5 /nobreak > nul

echo [2/2] Starting Spring Boot Backend (Port 8080)...
start "Spring Boot Backend (Port 8080)" cmd /k "cd backend && mvnw.cmd spring-boot:run"

echo.
echo ========================================================
echo Services are starting in dedicated background windows!
echo Web Application: http://localhost:8080
echo FastAPI Docs:    http://127.0.0.1:8000/docs
echo H2 DB Console:   http://localhost:8080/h2-console
echo ========================================================
pause
