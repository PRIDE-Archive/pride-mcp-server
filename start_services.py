#!/usr/bin/env python3
"""
Script to start both the PRIDE MCP server and web UI together.
"""

import subprocess
import sys
import time
import signal
import os
import threading
from pathlib import Path

def check_port_in_use(port):
    """Check if a port is already in use."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return False
    except OSError:
        return True

def kill_process_on_port(port):
    """Kill any process using the specified port."""
    try:
        import subprocess
        import os
        
        # Try to find process using the port with different methods
        pids = []
        
        # Method 1: Try lsof if available
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids.extend(result.stdout.strip().split('\n'))
        except FileNotFoundError:
            pass
        
        # Method 2: Try netstat if available
        try:
            result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTEN' in line:
                    # Extract PID from netstat output
                    parts = line.split()
                    if len(parts) > 6:
                        pid_part = parts[6]
                        if '/' in pid_part:
                            pid = pid_part.split('/')[0]
                            if pid.isdigit():
                                pids.append(pid)
        except FileNotFoundError:
            pass
        
        # Method 3: Try ss if available
        try:
            result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTEN' in line:
                    # Extract PID from ss output
                    if 'pid=' in line:
                        pid_start = line.find('pid=') + 4
                        pid_end = line.find(',', pid_start)
                        if pid_end == -1:
                            pid_end = line.find(' ', pid_start)
                        if pid_end != -1:
                            pid = line[pid_start:pid_end]
                            if pid.isdigit():
                                pids.append(pid)
        except FileNotFoundError:
            pass
        
        # Kill found processes
        if pids:
            for pid in pids:
                if pid and pid.isdigit():
                    print(f"🔄 Killing process {pid} on port {port}")
                    try:
                        os.kill(int(pid), 9)  # SIGKILL
                    except (OSError, ValueError):
                        pass  # Process might already be dead
            time.sleep(1)  # Give time for process to be killed
            return True
        else:
            print(f"⚠️  No process found using port {port}")
            return False
    except Exception as e:
        print(f"⚠️  Could not kill process on port {port}: {e}")
    return False

def print_output(process, prefix):
    """Consume process output to prevent blocking."""
    for line in iter(process.stdout.readline, ''):
        if line:
            # Don't print anything - just consume the output to prevent blocking
            pass

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

def start_api_server():
    """Start the PRIDE API server."""
    print("🚀 Starting PRIDE API Server...")
    
    # Check if port 9000 is already in use
    if check_port_in_use(9000):
        print("⚠️  Port 9000 is already in use. Checking if it's our own server...")
        # Try to connect to the existing server to see if it's working
        try:
            import urllib.request
            response = urllib.request.urlopen('http://localhost:9000/health', timeout=5)
            if response.getcode() == 200:
                print("✅ API Server is already running and responding on http://0.0.0.0:9000")
                return None  # Server is already running
        except:
            pass
        
        print("⚠️  Attempting to kill existing process...")
        kill_process_on_port(9000)
        time.sleep(2)  # Wait for port to be freed
    
    try:
        # Start the API server with real-time output
        api_process = subprocess.Popen([
            sys.executable, "server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
        # Start a thread to read and display output in real-time
        api_output_thread = threading.Thread(target=print_output, args=(api_process, "API"), daemon=True)
        api_output_thread.start()
        
        # Wait a moment for server to start
        time.sleep(5)
        
        if api_process.poll() is None:
            print("✅ PRIDE API Server started successfully on http://0.0.0.0:9000")
            return api_process
        else:
            stdout, stderr = api_process.communicate()
            print(f"❌ Failed to start API server: {stdout}")
            return None
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def start_mcp_server():
    """Start the PRIDE MCP server."""
    print("🚀 Starting PRIDE MCP Server...")
    
    # Check if port 9001 is already in use
    if check_port_in_use(9001):
        print("⚠️  Port 9001 is already in use. Checking if it's our own server...")
        # Try to connect to the existing server to see if it's working
        try:
            import urllib.request
            response = urllib.request.urlopen('http://localhost:9001/health', timeout=5)
            if response.getcode() == 200:
                print("✅ MCP Server is already running and responding on http://0.0.0.0:9001")
                return None  # Server is already running
        except:
            pass
        
        print("⚠️  Attempting to kill existing process...")
        kill_process_on_port(9001)
        time.sleep(2)  # Wait for port to be freed
    
    try:
        # Start the MCP server with real-time output
        mcp_process = subprocess.Popen([
            sys.executable, "mcp_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
        # Start a thread to read and display output in real-time
        mcp_output_thread = threading.Thread(target=print_output, args=(mcp_process, "MCP"), daemon=True)
        mcp_output_thread.start()
        
        # Wait a moment for server to start
        time.sleep(5)
        
        if mcp_process.poll() is None:
            print("✅ PRIDE MCP Server started successfully on http://0.0.0.0:9001")
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
    
    # Check if port 9090 is already in use
    if check_port_in_use(9090):
        print("⚠️  Port 9090 is already in use. Checking if it's our own server...")
        # Try to connect to the existing server to see if it's working
        try:
            import urllib.request
            response = urllib.request.urlopen('http://localhost:9090/', timeout=5)
            if response.getcode() == 200:
                print("✅ Web UI is already running and responding on http://0.0.0.0:9090")
                return None  # Server is already running
        except:
            pass
        
        print("⚠️  Attempting to kill existing process...")
        kill_process_on_port(9090)
        time.sleep(2)  # Wait for port to be freed
    
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
            "--server-url", "http://0.0.0.0:9001",
            "--port", "9090"
        ], cwd=client_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, bufsize=1, universal_newlines=True)
        
        # Start a thread to read and display output in real-time
        web_output_thread = threading.Thread(target=print_output, args=(web_process, "UI"), daemon=True)
        web_output_thread.start()
        
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

def start_analytics_ui():
    """Start the analytics dashboard."""
    print("📊 Starting Analytics Dashboard...")
    
    # Check if port 8080 is already in use
    if check_port_in_use(8080):
        print("⚠️  Port 8080 is already in use. Checking if it's our own server...")
        # Try to connect to the existing server to see if it's working
        try:
            import urllib.request
            response = urllib.request.urlopen('http://localhost:8080/', timeout=5)
            if response.getcode() == 200:
                print("✅ Analytics Dashboard is already running and responding on http://0.0.0.0:8080")
                return None  # Server is already running
        except:
            pass
        
        print("⚠️  Attempting to kill existing process...")
        kill_process_on_port(8080)
        time.sleep(2)  # Wait for port to be freed
    
    try:
        # Start the analytics server
        analytics_process = subprocess.Popen([
            sys.executable, "serve_analytics.py",
            "--port", "8080"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
        # Start a thread to read and display output in real-time
        analytics_output_thread = threading.Thread(target=print_output, args=(analytics_process, "Analytics"), daemon=True)
        analytics_output_thread.start()
        
        # Wait a moment for analytics to start
        time.sleep(5)
        
        if analytics_process.poll() is None:
            print("✅ Analytics Dashboard started successfully on http://0.0.0.0:8080")
            return analytics_process
        else:
            stdout, stderr = analytics_process.communicate()
            print(f"❌ Failed to start Analytics Dashboard: {stdout}")
            return None
    except Exception as e:
        print(f"❌ Error starting Analytics Dashboard: {e}")
        return None

def verify_services():
    """Verify all services are running."""
    print("\n🔍 Verifying all services are running...")
    services = [
        (9000, "API Server"),
        (9001, "MCP Server"),
        (9090, "UI Server"),
        (8080, "Analytics Server")
    ]
    
    all_running = True
    for port, name in services:
        if check_port_in_use(port):
            print(f"✅ {name} is running on port {port}")
        else:
            print(f"❌ {name} is NOT running on port {port}")
            all_running = False
    
    if all_running:
        print("🎉 All services are running successfully!")
    else:
        print("⚠️  Some services failed to start!")
    
    return all_running

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
    
    # Start API server
    api_process = start_api_server()
    if api_process is None:
        print("✅ API server is already running")
        api_process = None  # Ensure it's None for later checks
    elif not api_process:
        print("❌ Failed to start API server. Exiting.")
        sys.exit(1)
    
    # Start MCP server
    mcp_process = start_mcp_server()
    if mcp_process is None:
        print("✅ MCP server is already running")
        mcp_process = None  # Ensure it's None for later checks
    elif not mcp_process:
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
        print("   You can access the MCP server directly at http://0.0.0.0:9001")
    
    # Start Analytics Dashboard
    analytics_process = start_analytics_ui()
    if not analytics_process:
        print("⚠️  Failed to start Analytics Dashboard. Other services are still running.")
    
    # Verify all services are running
    verify_services()
    
    print("\n🎉 Services started successfully!")
    print("📋 Service URLs:")
    print("   API Server: http://0.0.0.0:9000")
    print("   MCP Server: http://0.0.0.0:9001")
    if web_process:
        print("   Professional UI: http://0.0.0.0:9090")
    if analytics_process:
        print("   Analytics Dashboard: http://0.0.0.0:8080")
    print("\n💡 Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process and api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
                
            if mcp_process and mcp_process.poll() is not None:
                print("❌ MCP server stopped unexpectedly")
                break
                
            if web_process and web_process.poll() is not None:
                print("❌ Professional UI stopped unexpectedly")
                break
                
            if analytics_process and analytics_process.poll() is not None:
                print("❌ Analytics Dashboard stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
    finally:
        # Clean up processes
        if api_process and api_process.poll() is None:
            api_process.terminate()
            api_process.wait()
            print("✅ API server stopped")
            
        if mcp_process and mcp_process.poll() is None:
            mcp_process.terminate()
            mcp_process.wait()
            print("✅ MCP server stopped")
            
        if web_process and web_process.poll() is None:
            web_process.terminate()
            web_process.wait()
            print("✅ Professional UI stopped")
            
        if analytics_process and analytics_process.poll() is None:
            analytics_process.terminate()
            analytics_process.wait()
            print("✅ Analytics Dashboard stopped")
        
        print("👋 All services stopped. Goodbye!")

if __name__ == "__main__":
    main() 