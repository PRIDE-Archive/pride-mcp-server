#!/usr/bin/env python3
"""
Separate MCP Server for PRIDE Archive tools.
Runs independently on port 9001.
"""

import uvicorn
import logging
from tools.pride_archive_public_api import streamable_http_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Start the MCP server on port 9001."""
    try:
        # Create the MCP app directly
        mcp_app = streamable_http_app()
        logger.info(f"✅ MCP app created successfully with {len(mcp_app.routes)} routes")
        
        print("🚀 Starting PRIDE MCP Server (MCP only)...")
        print("   MCP Server URL: http://0.0.0.0:9001")
        print("   MCP Endpoint: http://0.0.0.0:9001/")
        print("   Log Level: INFO")
        
        # Start the MCP server directly
        uvicorn.run(
            mcp_app, 
            host="0.0.0.0", 
            port=9001, 
            log_level="info", 
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start MCP server: {e}")
        raise

if __name__ == "__main__":
    main() 