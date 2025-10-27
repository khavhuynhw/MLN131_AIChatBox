@echo off
REM HCM Chatbot - Docker Build Script for Windows
REM Build all Docker images for the project

setlocal enabledelayedexpansion

echo 🐳 Building HCM Chatbot Docker Images...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Build Python AI Backend
echo [INFO] Building Python AI Backend...
docker build -t hcm-python-ai:latest ./backend
if errorlevel 1 (
    echo [ERROR] Failed to build Python AI Backend
    exit /b 1
)
echo [SUCCESS] Python AI Backend built successfully

REM Build .NET API
echo [INFO] Building .NET API...
docker build -t hcm-dotnet-api:latest ./dotnet-api/hcm-chatbot-api
if errorlevel 1 (
    echo [ERROR] Failed to build .NET API
    exit /b 1
)
echo [SUCCESS] .NET API built successfully

REM Build Node.js API
echo [INFO] Building Node.js API...
docker build -t hcm-nodejs-api:latest ./nodejs-api
if errorlevel 1 (
    echo [ERROR] Failed to build Node.js API
    exit /b 1
)
echo [SUCCESS] Node.js API built successfully

REM Build Frontend
echo [INFO] Building Frontend...
docker build -t hcm-frontend:latest ./frontend
if errorlevel 1 (
    echo [ERROR] Failed to build Frontend
    exit /b 1
)
echo [SUCCESS] Frontend built successfully

echo [SUCCESS] All Docker images built successfully! 🎉
echo.
echo Available images:
docker images | findstr hcm-

echo.
echo To run the application:
echo   docker-compose up -d
echo.
echo To run in development mode:
echo   docker-compose -f docker-compose.dev.yml up -d

