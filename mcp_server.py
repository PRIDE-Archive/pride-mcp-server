#!/usr/bin/env python3
"""
Separate MCP Server for PRIDE Archive tools.
Runs independently on port 9001.
"""

import uvicorn
import logging
import time
from datetime import datetime
from tools.pride_archive_public_api import streamable_http_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_server_startup():
    """Log server startup information"""
    logger.info("🚀 PRIDE MCP Server starting up")

def main():
    """Start the MCP server on port 9001."""
    start_time = time.time()
    
    try:
        log_server_startup()
        
        # Create the MCP app directly
        mcp_app = streamable_http_app()
        logger.info(f"✅ MCP app created successfully with {len(mcp_app.routes)} routes")
        
        print(f"🚀 Starting PRIDE MCP Server (MCP only)...")
        print(f"   MCP Server URL: http://0.0.0.0:9001")
        print(f"   MCP Endpoint: http://0.0.0.0:9001/")
        print(f"   Log Level: INFO")
        print(f"   Access Log: ENABLED")
        
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