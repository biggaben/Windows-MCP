# Use Windows Server Core as base image to support Windows-specific operations
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Set working directory
WORKDIR /app

# Install Python 3.13 via winget (if available) or download directly
# Note: This is a simplified approach - in production, you might want to use a Python base image
RUN powershell -Command \
    "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe' -OutFile 'python-installer.exe'; \
    Start-Process -FilePath 'python-installer.exe' -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1' -Wait; \
    Remove-Item 'python-installer.exe'"

# Install uv package manager
RUN powershell -Command "python -m pip install uv"

# Copy project files
COPY . .

# Install Python dependencies using uv
RUN powershell -Command "uv sync"

# Expose port for MCP server (if needed)
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV MCP_SERVER_NAME=windows-mcp

# Create a startup script
RUN powershell -Command \
    "echo 'uv run main.py' | Out-File -FilePath startup.cmd -Encoding ascii"

# Run the MCP server
CMD ["powershell", "-Command", "uv run main.py"]
