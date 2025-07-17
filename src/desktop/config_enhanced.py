# Enhanced Windows MCP Desktop Configuration
# Configuration file for advanced desktop interaction settings

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class WindowsDesktopConfig:
    """Configuration for Windows MCP Desktop Server"""
    
    # Server Configuration
    server_name: str = "windows-mcp-desktop"
    server_host: str = "localhost"
    server_port: int = 8000
    log_level: str = "INFO"
    
    # Desktop Interaction Settings
    desktop_mode: bool = True
    gui_timeout: int = 30
    click_delay: float = 0.1
    smart_wait: bool = True
    cursor_animation: bool = True
    
    # RDP Configuration
    rdp_enabled: bool = True
    rdp_port: int = 3389
    rdp_username: str = "mcpuser"
    rdp_password: str = "MCP@Windows2024!"
    
    # Screenshot Settings
    screenshot_format: str = "PNG"
    screenshot_quality: int = 95
    screenshot_cache_size: int = 100
    screenshot_dir: str = "screenshots"
    
    # Session Management
    session_timeout: int = 3600  # 1 hour
    session_dir: str = "sessions"
    max_sessions: int = 10
    
    # Performance Settings
    max_workers: int = 4
    memory_limit: str = "8G"
    cpu_limit: str = "4.0"
    
    # Security Settings
    secure_mode: bool = True
    admin_required: bool = False
    allowed_commands: List[str] = None
    blocked_commands: List[str] = None
    
    # Monitoring Settings
    monitoring_enabled: bool = True
    health_check_interval: int = 30
    resource_monitoring: bool = True
    
    # Windows-specific Settings
    windows_automation: bool = True
    ui_automation_depth: int = 5
    window_focus_timeout: int = 5
    
    # Logging Configuration
    log_dir: str = "logs"
    log_max_size: str = "10MB"
    log_max_files: int = 5
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Data Storage
    data_dir: str = "data"
    persistent_sessions: bool = True
    session_backup: bool = True
    
    def __post_init__(self):
        """Initialize configuration with environment variables"""
        # Override with environment variables if set
        self.server_name = os.getenv("MCP_SERVER_NAME", self.server_name)
        self.server_host = os.getenv("MCP_SERVER_HOST", self.server_host)
        self.server_port = int(os.getenv("MCP_SERVER_PORT", self.server_port))
        self.log_level = os.getenv("MCP_LOG_LEVEL", self.log_level)
        
        self.desktop_mode = os.getenv("WINDOWS_DESKTOP_MODE", str(self.desktop_mode)).lower() == "true"
        self.rdp_enabled = os.getenv("RDP_ENABLED", str(self.rdp_enabled)).lower() == "true"
        self.rdp_username = os.getenv("RDP_USERNAME", self.rdp_username)
        self.rdp_password = os.getenv("RDP_PASSWORD", self.rdp_password)
        
        self.monitoring_enabled = os.getenv("MONITORING_ENABLED", str(self.monitoring_enabled)).lower() == "true"
        self.secure_mode = os.getenv("SECURE_MODE", str(self.secure_mode)).lower() == "true"
        
        # Create directories if they don't exist
        self._create_directories()
        
        # Set up command restrictions
        self._setup_command_restrictions()
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.screenshot_dir,
            self.session_dir,
            self.log_dir,
            self.data_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _setup_command_restrictions(self):
        """Set up command restrictions for security"""
        if self.secure_mode:
            # Default blocked commands in secure mode
            if self.blocked_commands is None:
                self.blocked_commands = [
                    "format",
                    "del /f /q",
                    "rmdir /s /q",
                    "shutdown",
                    "restart",
                    "net user",
                    "net localgroup",
                    "reg delete",
                    "schtasks /delete",
                    "wmic process call terminate"
                ]
            
            # Default allowed commands
            if self.allowed_commands is None:
                self.allowed_commands = [
                    "dir",
                    "type",
                    "echo",
                    "Get-Process",
                    "Get-Service",
                    "Get-ChildItem",
                    "Test-NetConnection",
                    "Get-Counter",
                    "Get-CimInstance"
                ]
    
    def get_powershell_config(self) -> Dict[str, Any]:
        """Get PowerShell execution configuration"""
        return {
            "execution_policy": "RemoteSigned" if self.secure_mode else "Bypass",
            "timeout": 30,
            "admin_required": self.admin_required,
            "allowed_commands": self.allowed_commands,
            "blocked_commands": self.blocked_commands
        }
    
    def get_rdp_config(self) -> Dict[str, Any]:
        """Get RDP configuration"""
        return {
            "enabled": self.rdp_enabled,
            "port": self.rdp_port,
            "username": self.rdp_username,
            "password": self.rdp_password
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            "level": self.log_level,
            "format": self.log_format,
            "handlers": {
                "file": {
                    "filename": f"{self.log_dir}/windows-mcp-desktop.log",
                    "maxBytes": self._parse_size(self.log_max_size),
                    "backupCount": self.log_max_files
                },
                "console": {
                    "level": self.log_level
                }
            }
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return {
            "max_workers": self.max_workers,
            "memory_limit": self.memory_limit,
            "cpu_limit": self.cpu_limit,
            "gui_timeout": self.gui_timeout,
            "click_delay": self.click_delay
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "secure_mode": self.secure_mode,
            "admin_required": self.admin_required,
            "allowed_commands": self.allowed_commands,
            "blocked_commands": self.blocked_commands
        }
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Validate ports
        if not (1 <= self.server_port <= 65535):
            issues.append(f"Invalid server port: {self.server_port}")
        
        if not (1 <= self.rdp_port <= 65535):
            issues.append(f"Invalid RDP port: {self.rdp_port}")
        
        # Validate directories
        for directory in [self.screenshot_dir, self.session_dir, self.log_dir, self.data_dir]:
            if not Path(directory).exists():
                issues.append(f"Directory does not exist: {directory}")
        
        # Validate performance settings
        if self.max_workers < 1:
            issues.append("max_workers must be at least 1")
        
        if self.gui_timeout < 1:
            issues.append("gui_timeout must be at least 1 second")
        
        if self.click_delay < 0:
            issues.append("click_delay cannot be negative")
        
        # Validate security settings
        if self.secure_mode and not self.allowed_commands:
            issues.append("allowed_commands must be specified in secure mode")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "server": {
                "name": self.server_name,
                "host": self.server_host,
                "port": self.server_port,
                "log_level": self.log_level
            },
            "desktop": {
                "mode": self.desktop_mode,
                "gui_timeout": self.gui_timeout,
                "click_delay": self.click_delay,
                "smart_wait": self.smart_wait,
                "cursor_animation": self.cursor_animation
            },
            "rdp": self.get_rdp_config(),
            "security": self.get_security_config(),
            "performance": self.get_performance_config(),
            "logging": self.get_logging_config(),
            "monitoring": {
                "enabled": self.monitoring_enabled,
                "health_check_interval": self.health_check_interval,
                "resource_monitoring": self.resource_monitoring
            }
        }

# Global configuration instance
config = WindowsDesktopConfig()

# Configuration validation
def validate_environment():
    """Validate the environment configuration"""
    issues = config.validate_config()
    if issues:
        print("Configuration Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    return True

# Export configuration functions
def get_config() -> WindowsDesktopConfig:
    """Get the global configuration instance"""
    return config

def reload_config():
    """Reload configuration from environment"""
    global config
    config = WindowsDesktopConfig()
    return config

if __name__ == "__main__":
    # Test configuration
    print("Windows MCP Desktop Configuration")
    print("=" * 40)
    
    if validate_environment():
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has issues")
    
    print("\nConfiguration Summary:")
    print(f"Server: {config.server_name}:{config.server_port}")
    print(f"Desktop Mode: {config.desktop_mode}")
    print(f"RDP Enabled: {config.rdp_enabled}")
    print(f"Secure Mode: {config.secure_mode}")
    print(f"Monitoring: {config.monitoring_enabled}")
    print(f"Log Level: {config.log_level}")
