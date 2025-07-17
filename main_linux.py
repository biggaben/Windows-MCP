# Simplified main.py for Linux testing
from fastmcp import FastMCP
from textwrap import dedent

# Mock the Windows-specific imports to avoid errors
class MockDesktop:
    def launch_app(self, name):
        return f"Mock launch of {name} (not available in Linux)", 1

class MockCursor:
    pass

class MockWatchCursor:
    def start(self):
        pass
    def stop(self):
        pass

# Mock Windows-specific modules
import sys
from unittest.mock import MagicMock

# Mock the problematic imports
sys.modules['live_inspect.watch_cursor'] = MagicMock()
sys.modules['humancursor'] = MagicMock()
sys.modules['uiautomation'] = MagicMock()
sys.modules['pyautogui'] = MagicMock()
sys.modules['pyperclip'] = MagicMock()
sys.modules['src.desktop'] = MagicMock()

# Set up the MCP server
instructions = dedent('''
Linux-compatible Windows MCP server (limited functionality).
This version runs on Linux but has limited Windows desktop interaction capabilities.
Suitable for testing and development purposes.
''')

desktop = MockDesktop()
cursor = MockCursor()
watch_cursor = MockWatchCursor()

from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def lifespan(app: FastMCP):
    """Runs initialization code before the server starts and cleanup code after it shuts down."""
    try:
        watch_cursor.start()
        await asyncio.sleep(1)  # Simulate startup latency
        yield
    except Exception:
        pass
    finally:
        watch_cursor.stop()

mcp = FastMCP(name='windows-mcp-linux', instructions=instructions, lifespan=lifespan)

@mcp.tool(name='Launch-Tool', description='Mock launch tool for testing (Linux version)')
def launch_tool(name: str) -> str:
    """Mock launch tool that simulates launching an application."""
    return f'Mock: Would launch {name.title()} (not available in Linux container)'

@mcp.tool(name='State-Tool', description='Mock state tool for testing (Linux version)')
def state_tool(use_vision: bool = False) -> str:
    """Mock state tool that simulates getting desktop state."""
    return 'Mock: Desktop state not available in Linux container'

@mcp.tool(name='Screenshot-Tool', description='Mock screenshot tool for testing (Linux version)')
def screenshot_tool() -> str:
    """Mock screenshot tool that simulates taking a screenshot."""
    return 'Mock: Screenshot not available in Linux container'

@mcp.tool(name='Health-Check', description='Health check endpoint for container monitoring')
def health_check() -> str:
    """Health check endpoint for monitoring."""
    return 'Windows-MCP Linux version is running'

if __name__ == '__main__':
    print("Starting Windows-MCP Linux version...")
    print("This is a limited functionality version for testing purposes.")
    print("For full Windows desktop interaction, use the Windows version.")
    mcp.run()
