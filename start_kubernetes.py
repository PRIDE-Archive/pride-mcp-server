#!/usr/bin/env python3
"""
Kubernetes startup script for PRIDE MCP Server and UI.
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def load_env_config():
    """Load environment variables from config.env file."""
    config_file = Path("config.env")
    if config_file.exists():
        print("📁 Loading configuration from config.env...")
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ Configuration loaded")
    else:
        print("⚠️  config.env not found, using default settings")

def start_mcp_server():
    """Start the PRIDE MCP server on 0.0.0.0:9000."""
    print("🚀 Starting PRIDE MCP Server on 0.0.0.0:9000...")
    try:
        # Start the MCP server directly
        mcp_process = subprocess.Popen([
            sys.executable, "server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
        # Wait a moment for server to start
        time.sleep(5)
        
        if mcp_process.poll() is None:
            print("✅ PRIDE MCP Server started successfully on http://0.0.0.0:9000")
            return mcp_process
        else:
            stdout, stderr = mcp_process.communicate()
            print(f"❌ Failed to start MCP server: {stdout}")
            return None
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")
        return None

def start_web_ui():
    """Start the web UI on 0.0.0.0:9090."""
    print("🌐 Starting Professional UI on 0.0.0.0:9090...")
    try:
        # Start the professional UI directly
        env = os.environ.copy()
        env['PYTHONPATH'] = f"mcp_client_tools/src:{env.get('PYTHONPATH', '')}"
        
        web_process = subprocess.Popen([
            sys.executable, "-m", "mcp_client_tools.professional_ui", 
            "--server-url", "http://127.0.0.1:9000",
            "--port", "9090",
            "--host", "0.0.0.0"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, bufsize=1, universal_newlines=True)
        
        # Wait a moment for UI to start
        time.sleep(5)
        
        if web_process.poll() is None:
            print("✅ Professional UI started successfully on http://0.0.0.0:9090")
            return web_process
        else:
            stdout, stderr = web_process.communicate()
            print(f"❌ Failed to start Professional UI: {stdout}")
            return None
    except Exception as e:
        print(f"❌ Error starting Professional UI: {e}")
        return None

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print("\n🛑 Shutting down services...")
    sys.exit(0)

def main():
    """Main function to start both services."""
    print("🎯 PRIDE MCP Server + Web UI Starter (Kubernetes)")
    print("=" * 50)
    
    # Load configuration
    load_env_config()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start MCP server
    mcp_process = start_mcp_server()
    if not mcp_process:
        print("❌ Failed to start MCP server. Exiting.")
        sys.exit(1)
    
    # Start Professional UI
    web_process = start_web_ui()
    if not web_process:
        print("⚠️  Failed to start Professional UI. MCP server is still running.")
        print("   You can access the MCP server directly at http://0.0.0.0:9000")
    
    print("\n🎉 Services started successfully!")
    print("📋 Service URLs:")
    print("   🔧 MCP Server: http://0.0.0.0:9000")
    print("   🌐 Web UI: http://0.0.0.0:9090")
    print("   📊 Analytics: http://0.0.0.0:8080")
    print("\n🔄 Services are running. Press Ctrl+C to stop.")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        if mcp_process:
            mcp_process.terminate()
        if web_process:
            web_process.terminate()
        print("✅ Services stopped.")

if __name__ == "__main__":
    main() 