# Enhanced Windows MCP Server with Desktop Interaction Capabilities
# Extended main.py with additional Windows-specific tools and optimizations

import asyncio
import base64
import json
import logging
import os
import subprocess
import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pyautogui
import pygetwindow as gw
import pyperclip
import uiautomation as auto
from PIL import Image, ImageDraw, ImageFont
from fastmcp import FastMCP
from humancursor import SystemCursor
from live_inspect import inspect_windows
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure PyAutoGUI for Windows optimization
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  # Reduced pause for better performance

class WindowsDesktopMCP:
    """Enhanced Windows MCP Server with advanced desktop interaction capabilities"""
    
    def __init__(self):
        self.mcp = FastMCP("Windows Desktop MCP Server")
        self.cursor = SystemCursor()
        self.current_window = None
        self.screenshot_cache = {}
        self.session_data = {}
        
        # Register all tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all Windows desktop interaction tools"""
        
        # Enhanced clicking with smart targeting
        @self.mcp.tool()
        def enhanced_click(
            x: int = Field(description="X coordinate to click"),
            y: int = Field(description="Y coordinate to click"),
            button: str = Field(default="left", description="Mouse button: left, right, middle"),
            clicks: int = Field(default=1, description="Number of clicks"),
            interval: float = Field(default=0.1, description="Interval between clicks"),
            target_window: Optional[str] = Field(default=None, description="Target window title"),
            smart_wait: bool = Field(default=True, description="Wait for UI element to be ready")
        ) -> str:
            """Enhanced click with window targeting and smart waiting"""
            try:
                # Focus target window if specified
                if target_window:
                    windows = gw.getWindowsWithTitle(target_window)
                    if windows:
                        windows[0].activate()
                        time.sleep(0.2)  # Wait for window activation
                
                # Smart wait for UI readiness
                if smart_wait:
                    # Check if target area is accessible
                    screenshot = pyautogui.screenshot()
                    if screenshot.getpixel((x, y)) == (0, 0, 0):  # Likely loading/blocked
                        time.sleep(0.5)
                
                # Perform enhanced click
                if button == "left":
                    pyautogui.click(x, y, clicks=clicks, interval=interval, button='left')
                elif button == "right":
                    pyautogui.click(x, y, clicks=clicks, interval=interval, button='right')
                elif button == "middle":
                    pyautogui.click(x, y, clicks=clicks, interval=interval, button='middle')
                
                return f"Enhanced click performed at ({x}, {y}) with {button} button, {clicks} clicks"
                
            except Exception as e:
                logger.error(f"Enhanced click error: {e}")
                return f"Enhanced click failed: {str(e)}"
        
        # Advanced window management
        @self.mcp.tool()
        def window_manager(
            action: str = Field(description="Action: list, focus, minimize, maximize, close, move, resize"),
            window_title: Optional[str] = Field(default=None, description="Target window title"),
            x: Optional[int] = Field(default=None, description="X coordinate for move/resize"),
            y: Optional[int] = Field(default=None, description="Y coordinate for move/resize"),
            width: Optional[int] = Field(default=None, description="Width for resize"),
            height: Optional[int] = Field(default=None, description="Height for resize")
        ) -> str:
            """Advanced window management with comprehensive controls"""
            try:
                if action == "list":
                    windows = gw.getAllWindows()
                    window_list = []
                    for window in windows:
                        if window.title and window.visible:
                            window_list.append({
                                "title": window.title,
                                "position": f"({window.left}, {window.top})",
                                "size": f"{window.width}x{window.height}",
                                "active": window.isActive,
                                "minimized": window.isMinimized,
                                "maximized": window.isMaximized
                            })
                    return json.dumps(window_list, indent=2)
                
                if not window_title:
                    return "Window title required for this action"
                
                windows = gw.getWindowsWithTitle(window_title)
                if not windows:
                    return f"No window found with title: {window_title}"
                
                window = windows[0]
                
                if action == "focus":
                    window.activate()
                    return f"Focused window: {window_title}"
                elif action == "minimize":
                    window.minimize()
                    return f"Minimized window: {window_title}"
                elif action == "maximize":
                    window.maximize()
                    return f"Maximized window: {window_title}"
                elif action == "close":
                    window.close()
                    return f"Closed window: {window_title}"
                elif action == "move" and x is not None and y is not None:
                    window.moveTo(x, y)
                    return f"Moved window {window_title} to ({x}, {y})"
                elif action == "resize" and width is not None and height is not None:
                    window.resizeTo(width, height)
                    return f"Resized window {window_title} to {width}x{height}"
                
                return f"Action {action} completed for window: {window_title}"
                
            except Exception as e:
                logger.error(f"Window manager error: {e}")
                return f"Window manager failed: {str(e)}"
        
        # Enhanced UI automation
        @self.mcp.tool()
        def ui_automation(
            action: str = Field(description="Action: find_element, click_element, get_text, set_text"),
            element_type: Optional[str] = Field(default=None, description="Element type: Button, Edit, Text, etc."),
            element_name: Optional[str] = Field(default=None, description="Element name or title"),
            text_value: Optional[str] = Field(default=None, description="Text to input"),
            search_depth: int = Field(default=5, description="Search depth for elements"),
            timeout: int = Field(default=10, description="Timeout in seconds")
        ) -> str:
            """Advanced UI automation using Windows UI Automation"""
            try:
                if action == "find_element":
                    elements = []
                    
                    # Get the current foreground window
                    window = auto.GetForegroundWindow()
                    
                    # Find all controls of specified type
                    if element_type:
                        controls = window.GetChildren()
                        for control in controls:
                            if hasattr(control, 'ControlType') and element_type.lower() in control.ControlTypeName.lower():
                                elements.append({
                                    "name": control.Name,
                                    "type": control.ControlTypeName,
                                    "rect": control.BoundingRectangle,
                                    "enabled": control.IsEnabled,
                                    "visible": control.IsVisible
                                })
                    
                    return json.dumps(elements, indent=2)
                
                elif action == "click_element":
                    window = auto.GetForegroundWindow()
                    
                    # Find and click element
                    if element_name:
                        element = window.FindFirstByName(element_name)
                        if element:
                            element.Click()
                            return f"Clicked element: {element_name}"
                        else:
                            return f"Element not found: {element_name}"
                
                elif action == "get_text":
                    window = auto.GetForegroundWindow()
                    
                    if element_name:
                        element = window.FindFirstByName(element_name)
                        if element and hasattr(element, 'GetValuePattern'):
                            value_pattern = element.GetValuePattern()
                            return f"Text value: {value_pattern.Value}"
                    
                    return "Could not retrieve text"
                
                elif action == "set_text":
                    if not text_value:
                        return "Text value required"
                    
                    window = auto.GetForegroundWindow()
                    
                    if element_name:
                        element = window.FindFirstByName(element_name)
                        if element and hasattr(element, 'GetValuePattern'):
                            value_pattern = element.GetValuePattern()
                            value_pattern.SetValue(text_value)
                            return f"Set text '{text_value}' in element: {element_name}"
                    
                    return "Could not set text"
                
                return f"UI automation action {action} completed"
                
            except Exception as e:
                logger.error(f"UI automation error: {e}")
                return f"UI automation failed: {str(e)}"
        
        # Enhanced screenshot with annotations
        @self.mcp.tool()
        def enhanced_screenshot(
            region: Optional[str] = Field(default=None, description="Region as 'x,y,width,height' or 'fullscreen'"),
            annotate: bool = Field(default=False, description="Add annotations to screenshot"),
            highlight_cursor: bool = Field(default=False, description="Highlight cursor position"),
            window_title: Optional[str] = Field(default=None, description="Screenshot specific window"),
            format: str = Field(default="PNG", description="Image format: PNG, JPEG"),
            quality: int = Field(default=95, description="Image quality (1-100)")
        ) -> str:
            """Enhanced screenshot with annotations and window targeting"""
            try:
                screenshot = None
                
                # Handle different screenshot modes
                if window_title:
                    # Screenshot specific window
                    windows = gw.getWindowsWithTitle(window_title)
                    if windows:
                        window = windows[0]
                        screenshot = pyautogui.screenshot(region=(
                            window.left, window.top, window.width, window.height
                        ))
                    else:
                        return f"Window not found: {window_title}"
                
                elif region and region != "fullscreen":
                    # Screenshot specific region
                    try:
                        x, y, width, height = map(int, region.split(','))
                        screenshot = pyautogui.screenshot(region=(x, y, width, height))
                    except ValueError:
                        return "Invalid region format. Use 'x,y,width,height'"
                
                else:
                    # Full screen screenshot
                    screenshot = pyautogui.screenshot()
                
                # Add annotations if requested
                if annotate or highlight_cursor:
                    draw = ImageDraw.Draw(screenshot)
                    
                    if highlight_cursor:
                        # Highlight cursor position
                        cursor_pos = pyautogui.position()
                        cursor_x, cursor_y = cursor_pos
                        
                        # Adjust coordinates for region screenshots
                        if region and region != "fullscreen":
                            region_x, region_y = map(int, region.split(',')[:2])
                            cursor_x -= region_x
                            cursor_y -= region_y
                        
                        # Draw cursor highlight
                        draw.ellipse([
                            cursor_x - 10, cursor_y - 10,
                            cursor_x + 10, cursor_y + 10
                        ], outline='red', width=3)
                    
                    if annotate:
                        # Add timestamp
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        draw.text((10, 10), f"Screenshot: {timestamp}", fill='black')
                
                # Convert to base64
                buffer = BytesIO()
                screenshot.save(buffer, format=format, quality=quality)
                image_data = base64.b64encode(buffer.getvalue()).decode()
                
                # Cache screenshot
                cache_key = f"screenshot_{int(time.time())}"
                self.screenshot_cache[cache_key] = image_data
                
                return f"Screenshot captured and cached as {cache_key}. Size: {screenshot.size}"
                
            except Exception as e:
                logger.error(f"Enhanced screenshot error: {e}")
                return f"Enhanced screenshot failed: {str(e)}"
        
        # System resource monitoring
        @self.mcp.tool()
        def system_monitor(
            metric: str = Field(description="Metric: cpu, memory, disk, network, processes, services"),
            details: bool = Field(default=False, description="Include detailed information")
        ) -> str:
            """Monitor system resources and processes"""
            try:
                if metric == "processes":
                    # Get running processes
                    result = subprocess.run(
                        ["powershell", "-Command", "Get-Process | Select-Object ProcessName, Id, CPU, WorkingSet | ConvertTo-Json"],
                        capture_output=True, text=True
                    )
                    
                    if result.returncode == 0:
                        processes = json.loads(result.stdout)
                        return json.dumps(processes, indent=2)
                    else:
                        return f"Failed to get processes: {result.stderr}"
                
                elif metric == "services":
                    # Get Windows services
                    result = subprocess.run(
                        ["powershell", "-Command", "Get-Service | Select-Object DisplayName, Status, StartType | ConvertTo-Json"],
                        capture_output=True, text=True
                    )
                    
                    if result.returncode == 0:
                        services = json.loads(result.stdout)
                        return json.dumps(services, indent=2)
                    else:
                        return f"Failed to get services: {result.stderr}"
                
                elif metric == "cpu":
                    # Get CPU usage
                    result = subprocess.run(
                        ["powershell", "-Command", "Get-Counter '\\Processor(_Total)\\% Processor Time' -SampleInterval 1 -MaxSamples 1 | Select-Object -ExpandProperty CounterSamples | Select-Object CookedValue | ConvertTo-Json"],
                        capture_output=True, text=True
                    )
                    
                    if result.returncode == 0:
                        cpu_data = json.loads(result.stdout)
                        return f"CPU Usage: {cpu_data['CookedValue']:.2f}%"
                    else:
                        return f"Failed to get CPU usage: {result.stderr}"
                
                elif metric == "memory":
                    # Get memory usage
                    result = subprocess.run(
                        ["powershell", "-Command", "Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory | ConvertTo-Json"],
                        capture_output=True, text=True
                    )
                    
                    if result.returncode == 0:
                        memory_data = json.loads(result.stdout)
                        total_mb = memory_data['TotalVisibleMemorySize'] / 1024
                        free_mb = memory_data['FreePhysicalMemory'] / 1024
                        used_mb = total_mb - free_mb
                        usage_percent = (used_mb / total_mb) * 100
                        
                        return f"Memory Usage: {used_mb:.0f}MB / {total_mb:.0f}MB ({usage_percent:.1f}%)"
                    else:
                        return f"Failed to get memory usage: {result.stderr}"
                
                return f"System monitoring for {metric} completed"
                
            except Exception as e:
                logger.error(f"System monitor error: {e}")
                return f"System monitoring failed: {str(e)}"
        
        # Advanced PowerShell execution
        @self.mcp.tool()
        def advanced_powershell(
            command: str = Field(description="PowerShell command to execute"),
            execution_policy: str = Field(default="Bypass", description="Execution policy"),
            timeout: int = Field(default=30, description="Timeout in seconds"),
            capture_output: bool = Field(default=True, description="Capture command output"),
            run_as_admin: bool = Field(default=False, description="Run with elevated privileges")
        ) -> str:
            """Execute PowerShell commands with advanced options"""
            try:
                ps_args = ["powershell", "-ExecutionPolicy", execution_policy]
                
                if run_as_admin:
                    ps_args.extend(["-Command", f"Start-Process powershell -ArgumentList '-ExecutionPolicy {execution_policy} -Command \"{command}\"' -Verb RunAs -Wait"])
                else:
                    ps_args.extend(["-Command", command])
                
                result = subprocess.run(
                    ps_args,
                    capture_output=capture_output,
                    text=True,
                    timeout=timeout
                )
                
                if capture_output:
                    output = {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "return_code": result.returncode,
                        "command": command,
                        "execution_time": f"{timeout}s timeout"
                    }
                    return json.dumps(output, indent=2)
                else:
                    return f"PowerShell command executed with return code: {result.returncode}"
                
            except subprocess.TimeoutExpired:
                return f"PowerShell command timed out after {timeout} seconds"
            except Exception as e:
                logger.error(f"Advanced PowerShell error: {e}")
                return f"Advanced PowerShell execution failed: {str(e)}"
        
        # Session management
        @self.mcp.tool()
        def session_manager(
            action: str = Field(description="Action: save, load, list, clear"),
            session_name: Optional[str] = Field(default=None, description="Session name"),
            data: Optional[str] = Field(default=None, description="Session data to save")
        ) -> str:
            """Manage desktop interaction sessions"""
            try:
                if action == "save":
                    if not session_name or not data:
                        return "Session name and data required"
                    
                    self.session_data[session_name] = {
                        "data": data,
                        "timestamp": time.time(),
                        "windows": [{"title": w.title, "rect": (w.left, w.top, w.width, w.height)} 
                                   for w in gw.getAllWindows() if w.title]
                    }
                    return f"Session '{session_name}' saved"
                
                elif action == "load":
                    if not session_name:
                        return "Session name required"
                    
                    if session_name in self.session_data:
                        session = self.session_data[session_name]
                        return json.dumps(session, indent=2)
                    else:
                        return f"Session '{session_name}' not found"
                
                elif action == "list":
                    sessions = list(self.session_data.keys())
                    return json.dumps(sessions, indent=2)
                
                elif action == "clear":
                    if session_name:
                        if session_name in self.session_data:
                            del self.session_data[session_name]
                            return f"Session '{session_name}' cleared"
                        else:
                            return f"Session '{session_name}' not found"
                    else:
                        self.session_data.clear()
                        return "All sessions cleared"
                
                return f"Session management action {action} completed"
                
            except Exception as e:
                logger.error(f"Session manager error: {e}")
                return f"Session management failed: {str(e)}"
        
        # Keep original tools for backward compatibility
        @self.mcp.tool()
        def click_tool(x: int = Field(description="x coordinate to click"),
                      y: int = Field(description="y coordinate to click")) -> str:
            """Click at specified coordinates"""
            try:
                pyautogui.click(x, y)
                return f"Clicked at ({x}, {y})"
            except Exception as e:
                return f"Click failed: {str(e)}"
        
        @self.mcp.tool()
        def type_tool(text: str = Field(description="Text to type")) -> str:
            """Type text"""
            try:
                pyautogui.write(text)
                return f"Typed: {text}"
            except Exception as e:
                return f"Type failed: {str(e)}"
        
        @self.mcp.tool()
        def key_tool(key: str = Field(description="Key to press")) -> str:
            """Press a key"""
            try:
                pyautogui.press(key)
                return f"Pressed key: {key}"
            except Exception as e:
                return f"Key press failed: {str(e)}"
        
        @self.mcp.tool()
        def scroll_tool(direction: str = Field(description="Direction to scroll: up, down, left, right"),
                       amount: int = Field(default=3, description="Amount to scroll")) -> str:
            """Scroll in specified direction"""
            try:
                if direction == "up":
                    pyautogui.scroll(amount)
                elif direction == "down":
                    pyautogui.scroll(-amount)
                elif direction == "left":
                    pyautogui.hscroll(-amount)
                elif direction == "right":
                    pyautogui.hscroll(amount)
                return f"Scrolled {direction} by {amount}"
            except Exception as e:
                return f"Scroll failed: {str(e)}"
        
        @self.mcp.tool()
        def screenshot_tool() -> str:
            """Take a screenshot"""
            try:
                screenshot = pyautogui.screenshot()
                timestamp = int(time.time())
                buffer = BytesIO()
                screenshot.save(buffer, format='PNG')
                image_data = base64.b64encode(buffer.getvalue()).decode()
                return f"Screenshot taken at {timestamp}. Size: {screenshot.size}"
            except Exception as e:
                return f"Screenshot failed: {str(e)}"
        
        @self.mcp.tool()
        def get_clipboard() -> str:
            """Get clipboard content"""
            try:
                content = pyperclip.paste()
                return f"Clipboard content: {content}"
            except Exception as e:
                return f"Clipboard read failed: {str(e)}"
        
        @self.mcp.tool()
        def set_clipboard(text: str = Field(description="Text to copy to clipboard")) -> str:
            """Set clipboard content"""
            try:
                pyperclip.copy(text)
                return f"Copied to clipboard: {text}"
            except Exception as e:
                return f"Clipboard write failed: {str(e)}"
        
        @self.mcp.tool()
        def get_screen_size() -> str:
            """Get screen dimensions"""
            try:
                screen_size = pyautogui.size()
                return f"Screen size: {screen_size.width}x{screen_size.height}"
            except Exception as e:
                return f"Screen size failed: {str(e)}"
        
        @self.mcp.tool()
        def get_mouse_position() -> str:
            """Get current mouse position"""
            try:
                pos = pyautogui.position()
                return f"Mouse position: ({pos.x}, {pos.y})"
            except Exception as e:
                return f"Mouse position failed: {str(e)}"
        
        @self.mcp.tool()
        def launch_app(app_name: str = Field(description="Application name or path")) -> str:
            """Launch an application"""
            try:
                subprocess.Popen(app_name, shell=True)
                return f"Launched application: {app_name}"
            except Exception as e:
                return f"Launch failed: {str(e)}"
        
        @self.mcp.tool()
        def run_powershell(command: str = Field(description="PowerShell command to run")) -> str:
            """Run PowerShell command"""
            try:
                result = subprocess.run(["powershell", "-Command", command], 
                                      capture_output=True, text=True, timeout=30)
                return f"PowerShell output:\n{result.stdout}\nErrors:\n{result.stderr}"
            except subprocess.TimeoutExpired:
                return "PowerShell command timed out"
            except Exception as e:
                return f"PowerShell failed: {str(e)}"
        
        @self.mcp.tool()
        def inspect_window() -> str:
            """Inspect current window structure"""
            try:
                windows_info = inspect_windows()
                return json.dumps(windows_info, indent=2, default=str)
            except Exception as e:
                return f"Window inspection failed: {str(e)}"
    
    def run(self):
        """Run the MCP server"""
        logger.info("Starting Windows Desktop MCP Server...")
        logger.info("Server supports enhanced desktop interaction capabilities")
        logger.info("Available tools: enhanced_click, window_manager, ui_automation, enhanced_screenshot, system_monitor, advanced_powershell, session_manager, and all original tools")
        
        try:
            self.mcp.run()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    server = WindowsDesktopMCP()
    server.run()
