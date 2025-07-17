# Windows MCP Desktop Container Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying the Windows MCP server with enhanced desktop interaction capabilities using Docker containers.

## Prerequisites

### System Requirements
- Windows 10/11 Pro or Windows Server 2019/2022
- Docker Desktop for Windows (latest version)
- Hyper-V enabled
- At least 8GB RAM and 4 CPU cores
- Administrator privileges

### Docker Configuration
1. **Switch to Windows Container Mode**
   ```powershell
   & "C:\Program Files\Docker\Docker\DockerCli.exe" -SwitchDaemon
   ```

2. **Verify Windows Container Support**
   ```powershell
   docker version
   docker info
   ```

## Quick Start

### 1. Build the Enhanced Desktop Image
```powershell
# Navigate to project directory
cd "C:\Users\David\Code\LLM Agentic Development\Windows-MCP"

# Build the enhanced desktop image
docker build -f Dockerfile.desktop -t windows-mcp-desktop:latest .
```

### 2. Run with Docker Compose
```powershell
# Start the complete stack
docker-compose -f docker-compose.desktop.yml up -d

# View logs
docker-compose -f docker-compose.desktop.yml logs -f windows-mcp-desktop
```

### 3. Access the Container
- **MCP Server**: `http://localhost:8000`
- **RDP Access**: `localhost:3389`
  - Username: `mcpuser`
  - Password: `MCP@Windows2024!`

## Advanced Deployment Options

### Manual Container Run
```powershell
# Run with full configuration
docker run -d \
  --name windows-mcp-desktop \
  --platform windows \
  --isolation hyperv \
  -p 8000:8000 \
  -p 3389:3389 \
  -e MCP_SERVER_NAME=windows-mcp-desktop \
  -e PYTHONUNBUFFERED=1 \
  -e WINDOWS_DESKTOP_MODE=true \
  -e RDP_ENABLED=true \
  -v ${PWD}/data:C:\app\data \
  -v ${PWD}/logs:C:\app\logs \
  -v ${PWD}/screenshots:C:\app\screenshots \
  -v ${PWD}/sessions:C:\app\sessions \
  --memory 8g \
  --cpus 4 \
  windows-mcp-desktop:latest
```

### Production Deployment
```powershell
# Create production configuration
docker run -d \
  --name windows-mcp-desktop-prod \
  --platform windows \
  --isolation hyperv \
  --restart unless-stopped \
  -p 8000:8000 \
  -p 3389:3389 \
  -e MCP_SERVER_NAME=windows-mcp-desktop-prod \
  -e MCP_LOG_LEVEL=INFO \
  -e WINDOWS_DESKTOP_MODE=true \
  -e RDP_ENABLED=true \
  --memory 8g \
  --cpus 4 \
  --security-opt no-new-privileges \
  --health-cmd "powershell -Command Test-NetConnection -ComputerName localhost -Port 8000" \
  --health-interval 30s \
  --health-timeout 10s \
  --health-retries 3 \
  windows-mcp-desktop:latest
```

## Enhanced Features

### Desktop Interaction Capabilities
- **Enhanced Click**: Smart targeting with window focus
- **Window Management**: Comprehensive window controls
- **UI Automation**: Windows UI Automation integration
- **Enhanced Screenshots**: Annotations and window targeting
- **System Monitoring**: Resource and process monitoring
- **Advanced PowerShell**: Enhanced command execution
- **Session Management**: Desktop interaction sessions

### RDP Access
The container includes RDP server for remote desktop access:
- Connect using Windows Remote Desktop Client
- Server: `localhost:3389`
- Username: `mcpuser`
- Password: `MCP@Windows2024!`

### Security Features
- Hyper-V isolation for enhanced security
- Non-root user execution
- Security options configured
- Firewall rules for RDP
- Secure password configuration

## Monitoring and Debugging

### Health Checks
```powershell
# Check container health
docker ps --filter "name=windows-mcp-desktop"

# View health check logs
docker inspect windows-mcp-desktop | findstr -i health

# Manual health check
docker exec windows-mcp-desktop powershell -Command "Test-NetConnection -ComputerName localhost -Port 8000"
```

### Log Management
```powershell
# View container logs
docker logs windows-mcp-desktop

# Follow logs in real-time
docker logs -f windows-mcp-desktop

# View specific log lines
docker logs --tail 100 windows-mcp-desktop
```

### Performance Monitoring
```powershell
# Container resource usage
docker stats windows-mcp-desktop

# Detailed container inspection
docker inspect windows-mcp-desktop
```

## Troubleshooting

### Common Issues

1. **Container Won't Start**
   - Verify Windows container mode is enabled
   - Check Hyper-V is running
   - Ensure sufficient resources available

2. **RDP Connection Issues**
   - Verify port 3389 is exposed
   - Check Windows Firewall settings
   - Confirm RDP service is running in container

3. **Desktop Interaction Issues**
   - Verify GUI applications can run
   - Check Windows desktop session
   - Ensure proper isolation mode

### Debug Commands
```powershell
# Enter container for debugging
docker exec -it windows-mcp-desktop powershell

# Check running processes
docker exec windows-mcp-desktop powershell -Command "Get-Process"

# Check services
docker exec windows-mcp-desktop powershell -Command "Get-Service"

# Check network connectivity
docker exec windows-mcp-desktop powershell -Command "Test-NetConnection -ComputerName localhost -Port 8000"
```

## Scaling and Performance

### Resource Optimization
- Adjust memory and CPU limits based on workload
- Use multi-stage builds for smaller images
- Implement container monitoring

### Load Balancing
```powershell
# Run multiple instances
docker run -d --name windows-mcp-desktop-1 -p 8001:8000 -p 3390:3389 windows-mcp-desktop:latest
docker run -d --name windows-mcp-desktop-2 -p 8002:8000 -p 3391:3389 windows-mcp-desktop:latest
```

## Security Considerations

### Network Security
- Use Docker networks for isolation
- Implement proper firewall rules
- Consider VPN access for production

### Container Security
- Regular image updates
- Vulnerability scanning
- Principle of least privilege

### Data Protection
- Encrypt sensitive data volumes
- Implement backup strategies
- Monitor access logs

## Maintenance

### Updates
```powershell
# Update base image
docker pull mcr.microsoft.com/windows/servercore:ltsc2022

# Rebuild image
docker build -f Dockerfile.desktop -t windows-mcp-desktop:latest .

# Update running containers
docker-compose -f docker-compose.desktop.yml pull
docker-compose -f docker-compose.desktop.yml up -d
```

### Backup
```powershell
# Backup container data
docker run --rm -v windows-mcp-desktop_data:/source -v ${PWD}/backup:/backup windows-mcp-desktop:latest powershell -Command "Copy-Item -Path /source/* -Destination /backup -Recurse"
```

### Cleanup
```powershell
# Remove unused containers and images
docker system prune -f

# Remove specific containers
docker-compose -f docker-compose.desktop.yml down
docker rmi windows-mcp-desktop:latest
```

## Support

For issues and questions:
1. Check container logs
2. Review troubleshooting section
3. Verify system requirements
4. Test with minimal configuration

## License

This deployment guide is part of the Windows-MCP project. See LICENSE file for details.
