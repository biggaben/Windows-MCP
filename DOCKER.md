# Docker Setup for Windows-MCP

This directory contains Docker configuration files to containerize the Windows-MCP server.

## Files

- `Dockerfile` - Main Dockerfile using Windows Server Core
- `Dockerfile.python` - Alternative Dockerfile using Python base image (recommended)
- `docker-compose.yml` - Docker Compose configuration
- `.dockerignore` - Files to exclude from Docker build context
- `docker-build.sh` - Build script for Unix-like systems
- `docker-build.bat` - Build script for Windows

## Prerequisites

1. **Docker Desktop** with Windows container support
2. **Windows containers** enabled in Docker Desktop
3. At least 4GB RAM allocated to Docker
4. Windows 10/11 or Windows Server 2019/2022

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and run using Docker Compose
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Stop the service
docker-compose down
```

### Using Build Scripts

**Windows:**
```cmd
# Build and run with default settings
docker-build.bat

# Build only (don't run)
docker-build.bat --build-only

# Use Python base image and custom port
docker-build.bat --python-base --port 8080
```

**Unix/Linux/macOS:**
```bash
# Make script executable
chmod +x docker-build.sh

# Build and run with default settings
./docker-build.sh

# Build only (don't run)
./docker-build.sh --build-only

# Use Python base image and custom port
./docker-build.sh --python-base --port 8080
```

### Manual Docker Commands

```bash
# Build the image
docker build -t windows-mcp .

# Run the container
docker run -d \
  --name windows-mcp-server \
  --platform windows \
  -p 8000:8000 \
  --isolation process \
  --memory 2g \
  --cpus 2 \
  --restart unless-stopped \
  windows-mcp
```

## Configuration

### Environment Variables

- `PYTHONPATH` - Python path (default: /app)
- `MCP_SERVER_NAME` - Server name (default: windows-mcp)
- `PYTHONUNBUFFERED` - Disable Python output buffering

### Port Mapping

- Default: `8000:8000`
- Change host port: `-p 8080:8000`

### Resource Limits

- Memory: 2GB (adjustable)
- CPU: 2 cores (adjustable)

## Dockerfile Options

### Dockerfile (Server Core)
- Uses Windows Server Core base image
- Installs Python manually
- Larger image size but more control

### Dockerfile.python (Recommended)
- Uses official Python Windows image
- Smaller and more optimized
- Better caching layers

## Monitoring

### Health Check
```bash
# Check container health
docker inspect windows-mcp-server | grep -A 5 "Health"

# Manual health check
docker exec windows-mcp-server powershell -Command "Test-NetConnection -ComputerName localhost -Port 8000"
```

### Logs
```bash
# View logs
docker logs windows-mcp-server

# Follow logs
docker logs -f windows-mcp-server

# View last 50 lines
docker logs --tail 50 windows-mcp-server
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   - Ensure Windows containers are enabled in Docker Desktop
   - Check available memory and CPU resources
   - Verify port is not already in use

2. **Build failures**
   - Clear Docker build cache: `docker system prune -a`
   - Ensure all dependencies are available
   - Check network connectivity for package downloads

3. **Permission issues**
   - Run Docker Desktop as administrator
   - Check Windows container isolation mode

### Debugging

```bash
# Enter container for debugging
docker exec -it windows-mcp-server powershell

# Check running processes
docker exec windows-mcp-server powershell -Command "Get-Process"

# Check network connectivity
docker exec windows-mcp-server powershell -Command "Test-NetConnection -ComputerName host.docker.internal -Port 8000"
```

## Important Notes

- **Windows Container Limitations**: Windows containers have different capabilities than Linux containers
- **GUI Applications**: Windows-MCP interacts with the desktop, which may be limited in containerized environments
- **Host System Access**: Some Windows-MCP features may require additional configuration for container access to host system
- **Performance**: Container performance may be lower than native installation due to virtualization overhead

## Integration with MCP Clients

When running in Docker, configure your MCP client to connect to:
- **Host**: `localhost` (or Docker host IP)
- **Port**: `8000` (or configured port)
- **Protocol**: HTTP/WebSocket as supported by Windows-MCP

## Production Considerations

1. **Security**: Run with least privilege principles
2. **Monitoring**: Implement proper logging and monitoring
3. **Updates**: Regular image updates for security patches
4. **Backup**: Backup any persistent data volumes
5. **Scaling**: Consider orchestration for multiple instances

For more information about Windows-MCP, see the main [README.md](../README.md).
