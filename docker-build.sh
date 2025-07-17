#!/bin/bash

# Docker build and run script for Windows-MCP
# This script helps build and run the Windows-MCP Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if running on Windows
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "cygwin" && "$OSTYPE" != "win32" ]]; then
    print_warning "This Windows-MCP container is designed for Windows. Running on other platforms may have limitations."
fi

# Default values
IMAGE_NAME="windows-mcp"
CONTAINER_NAME="windows-mcp-server"
PORT=8000
BUILD_ONLY=false
USE_PYTHON_BASE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--build-only)
            BUILD_ONLY=true
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --python-base)
            USE_PYTHON_BASE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -b, --build-only    Only build the image, don't run"
            echo "  -p, --port PORT     Set the port (default: 8000)"
            echo "  --python-base       Use Python base image instead of Server Core"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build the Docker image
print_status "Building Docker image..."
if [ "$USE_PYTHON_BASE" = true ]; then
    docker build -f Dockerfile.python -t $IMAGE_NAME .
else
    docker build -t $IMAGE_NAME .
fi

if [ $? -eq 0 ]; then
    print_status "Docker image built successfully!"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Exit if build-only mode
if [ "$BUILD_ONLY" = true ]; then
    print_status "Build complete. Exiting as requested."
    exit 0
fi

# Stop and remove existing container if it exists
if docker ps -a --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    print_status "Stopping and removing existing container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Run the container
print_status "Starting Windows-MCP container on port $PORT..."
docker run -d \
    --name $CONTAINER_NAME \
    --platform windows \
    -p $PORT:8000 \
    --isolation process \
    --memory 2g \
    --cpus 2 \
    --restart unless-stopped \
    $IMAGE_NAME

if [ $? -eq 0 ]; then
    print_status "Container started successfully!"
    print_status "Windows-MCP is now running on port $PORT"
    print_status "You can check the logs with: docker logs $CONTAINER_NAME"
    print_status "You can stop the container with: docker stop $CONTAINER_NAME"
else
    print_error "Failed to start container"
    exit 1
fi

# Show container status
print_status "Container status:"
docker ps --filter "name=$CONTAINER_NAME"
