@echo off
REM Build and tag Docker images for MLN131 Chatbot services
REM Usage: scripts\build-images.bat [push]

setlocal enabledelayedexpansion

REM Registry configuration
set REGISTRY=mln131
set VERSION=latest

echo Building Docker images for MLN131 Chatbot services...

REM Build postgres image
echo Building postgres image...
docker build -t %REGISTRY%/postgres:%VERSION% -f .\database\Dockerfile .\database
if %errorlevel% neq 0 (
    echo Error building postgres image
    exit /b 1
)
echo ✓ postgres image built successfully

REM Build python-ai image
echo Building python-ai image...
docker build -t %REGISTRY%/python-ai:%VERSION% -f .\backend\Dockerfile .\backend
if %errorlevel% neq 0 (
    echo Error building python-ai image
    exit /b 1
)
echo ✓ python-ai image built successfully

REM Build dotnet-api image
echo Building dotnet-api image...
docker build -t %REGISTRY%/dotnet-api:%VERSION% -f .\dotnet-api\Dockerfile .\dotnet-api
if %errorlevel% neq 0 (
    echo Error building dotnet-api image
    exit /b 1
)
echo ✓ dotnet-api image built successfully

REM Build nodejs-api image
echo Building nodejs-api image...
docker build -t %REGISTRY%/nodejs-api:%VERSION% -f .\nodejs-api\Dockerfile .\nodejs-api
if %errorlevel% neq 0 (
    echo Error building nodejs-api image
    exit /b 1
)
echo ✓ nodejs-api image built successfully

REM Build frontend image
echo Building frontend image...
docker build -t %REGISTRY%/frontend:%VERSION% -f .\frontend\Dockerfile .\frontend
if %errorlevel% neq 0 (
    echo Error building frontend image
    exit /b 1
)
echo ✓ frontend image built successfully

echo All images built successfully!

REM Push images if argument is provided
if "%1"=="push" (
    echo Pushing images to registry...
    
    echo Pushing postgres image...
    docker push %REGISTRY%/postgres:%VERSION%
    if %errorlevel% neq 0 (
        echo Error pushing postgres image
        exit /b 1
    )
    echo ✓ postgres image pushed successfully
    
    echo Pushing python-ai image...
    docker push %REGISTRY%/python-ai:%VERSION%
    if %errorlevel% neq 0 (
        echo Error pushing python-ai image
        exit /b 1
    )
    echo ✓ python-ai image pushed successfully
    
    echo Pushing dotnet-api image...
    docker push %REGISTRY%/dotnet-api:%VERSION%
    if %errorlevel% neq 0 (
        echo Error pushing dotnet-api image
        exit /b 1
    )
    echo ✓ dotnet-api image pushed successfully
    
    echo Pushing nodejs-api image...
    docker push %REGISTRY%/nodejs-api:%VERSION%
    if %errorlevel% neq 0 (
        echo Error pushing nodejs-api image
        exit /b 1
    )
    echo ✓ nodejs-api image pushed successfully
    
    echo Pushing frontend image...
    docker push %REGISTRY%/frontend:%VERSION%
    if %errorlevel% neq 0 (
        echo Error pushing frontend image
        exit /b 1
    )
    echo ✓ frontend image pushed successfully
    
    echo All images pushed successfully!
)

echo Done!
