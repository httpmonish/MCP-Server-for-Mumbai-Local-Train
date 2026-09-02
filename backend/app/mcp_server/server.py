"""Proxy module exposing MCP server app under app.mcp_server.server namespace."""
try:
    from ...mcp_server.server import app
except Exception:
    try:
        from mcp_server.server import app
    except Exception:
        from backend.mcp_server.server import app

__all__ = ["app"]
