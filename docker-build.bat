@echo off
REM Docker build and run script for Windows-MCP (Windows batch version)
REM This script helps build and run the Windows-MCP Docker container

setlocal enabledelayedexpansion

REM Default values
set IMAGE_NAME=windows-mcp
set CONTAINER_NAME=windows-mcp-server
set PORT=8000
set BUILD_ONLY=false
set USE_PYTHON_BASE=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="-b" (
    set BUILD_ONLY=true
    shift
    goto :parse_args
)
if "%~1"=="--build-only" (
    set BUILD_ONLY=true
    shift
    goto :parse_args
)
if "%~1"=="-p" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--python-base" (
    set USE_PYTHON_BASE=true
    shift
    goto :parse_args
)
if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help
echo Unknown option: %~1
exit /b 1

:show_help
echo Usage: %~nx0 [OPTIONS]
echo Options:
echo   -b, --build-only    Only build the image, don't run
echo   -p, --port PORT     Set the port (default: 8000)
echo   --python-base       Use Python base image instead of Server Core
echo   -h, --help          Show this help message
exit /b 0

:end_parse

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Build the Docker image
echo [INFO] Building Docker image...
if "%USE_PYTHON_BASE%"=="true" (
    docker build -f Dockerfile.python -t %IMAGE_NAME% .
) else (
    docker build -t %IMAGE_NAME% .
)

if errorlevel 1 (
    echo [ERROR] Failed to build Docker image
    exit /b 1
)

echo [INFO] Docker image built successfully!

REM Exit if build-only mode
if "%BUILD_ONLY%"=="true" (
    echo [INFO] Build complete. Exiting as requested.
    exit /b 0
)

REM Stop and remove existing container if it exists
docker ps -a --filter "name=%CONTAINER_NAME%" --format "{{.Names}}" | findstr /c:"%CONTAINER_NAME%" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Stopping and removing existing container...
    docker stop %CONTAINER_NAME%
    docker rm %CONTAINER_NAME%
)

REM Run the container
echo [INFO] Starting Windows-MCP container on port %PORT%...
docker run -d ^
    --name %CONTAINER_NAME% ^
    --platform windows ^
    -p %PORT%:8000 ^
    --isolation process ^
    --memory 2g ^
    --cpus 2 ^
    --restart unless-stopped ^
    %IMAGE_NAME%

if errorlevel 1 (
    echo [ERROR] Failed to start container
    exit /b 1
)

echo [INFO] Container started successfully!
echo [INFO] Windows-MCP is now running on port %PORT%
echo [INFO] You can check the logs with: docker logs %CONTAINER_NAME%
echo [INFO] You can stop the container with: docker stop %CONTAINER_NAME%

REM Show container status
echo [INFO] Container status:
docker ps --filter "name=%CONTAINER_NAME%"
