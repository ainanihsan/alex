"""
MCP server configurations for the Alex Researcher
"""
from agents.mcp import MCPServerStdio


def create_playwright_mcp_server(timeout_seconds=60):
    """Create a Playwright MCP server instance for web browsing.
    
    Args:
        timeout_seconds: Client session timeout in seconds (default: 60)
        
    Returns:
        MCPServerStdio instance configured for Playwright
    """
    # Arguments for the MCP server
    args = [
        "@playwright/mcp",
        "--headless",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--ignore-https-errors",
    ]
    
    params = {
        "command": "npx",
        "args": args
    }
    
    return MCPServerStdio(params=params, client_session_timeout_seconds=timeout_seconds)
    
    return MCPServerStdio(params=params, client_session_timeout_seconds=timeout_seconds)