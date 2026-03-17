"""
MCP server entrypoint.

Run this file to start the local 'itick-api' MCP server.
"""

from MCP.itick_mcp import app


if __name__ == "__main__":
    app.run()

