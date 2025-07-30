#!/usr/bin/env python3
"""
Script to start both the PRIDE MCP server and web UI together.
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
    """Start the PRIDE MCP server."""
    print("🚀 Starting PRIDE MCP Server...")
    try:
        # Start the MCP server with real-time output
        mcp_process = subprocess.Popen([
            sys.executable, "server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        if mcp_process.poll() is None:
            print("✅ PRIDE MCP Server started successfully on http://127.0.0.1:9000")
            return mcp_process
        else:
            stdout, stderr = mcp_process.communicate()
            print(f"❌ Failed to start MCP server: {stdout}")
            return None
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")
        return None

def start_web_ui():
    """Start the web UI from the client module."""
    print("🌐 Starting Professional UI...")
    try:
        # Try to install the client module in development mode first
        client_dir = Path("mcp_client_tools")
        if not client_dir.exists():
            print("❌ Client module not found. Please ensure mcp_client_tools directory exists.")
            return None
        
        # Start the professional UI directly with real-time output
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{client_dir}/src:{env.get('PYTHONPATH', '')}"
        
        web_process = subprocess.Popen([
            sys.executable, "-m", "mcp_client_tools.professional_ui", 
            "--server-url", "http://127.0.0.1:9000",
            "--port", "9090"
        ], cwd=client_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, bufsize=1, universal_newlines=True)
        
        # Wait a moment for UI to start
        time.sleep(3)
        
        if web_process.poll() is None:
            print("✅ Professional UI started successfully on http://127.0.0.1:9090")
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
    print("🎯 PRIDE MCP Server + Web UI Starter")
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
    
    # Check AI configuration
    ai_provider = None
    if os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here":
        ai_provider = "Gemini"
    elif os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here":
        ai_provider = "OpenAI"
    elif os.getenv("CLAUDE_API_KEY") and os.getenv("CLAUDE_API_KEY") != "your_claude_api_key_here":
        ai_provider = "Claude"
    
    if ai_provider:
        print(f"🤖 AI Provider: {ai_provider}")
    else:
        print("⚠️  No AI API key configured. Edit config.env to add your API key.")
    
    # Start Professional UI
    web_process = start_web_ui()
    if not web_process:
        print("⚠️  Failed to start Professional UI. MCP server is still running.")
        print("   You can access the MCP server directly at http://127.0.0.1:9000")
    
    print("\n🎉 Services started successfully!")
    print("📋 Service URLs:")
    print("   MCP Server: http://127.0.0.1:9000")
    if web_process:
        print("   Professional UI: http://127.0.0.1:9090")
    print("\n💡 Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if mcp_process.poll() is not None:
                print("❌ MCP server stopped unexpectedly")
                break
                
            if web_process and web_process.poll() is not None:
                print("❌ AI Conversational UI stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
    finally:
        # Clean up processes
        if mcp_process and mcp_process.poll() is None:
            mcp_process.terminate()
            mcp_process.wait()
            print("✅ MCP server stopped")
            
        if web_process and web_process.poll() is None:
            web_process.terminate()
            web_process.wait()
            print("✅ AI Conversational UI stopped")
        
        print("👋 All services stopped. Goodbye!")

if __name__ == "__main__":
    main() 