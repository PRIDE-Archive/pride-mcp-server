#!/usr/bin/env python3
"""
Simple HTTP server to serve the analytics dashboard.
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

def serve_analytics_dashboard(port=8080):
    """Serve the analytics dashboard on the specified port."""
    
    # Change to the directory containing the HTML file
    os.chdir(Path(__file__).parent)
    
    # Create a simple HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 Analytics Dashboard Server")
        print(f"   URL: http://localhost:{port}/analytics_dashboard.html")
        print(f"   Press Ctrl+C to stop")
        
        # Open the dashboard in the default browser
        webbrowser.open(f"http://localhost:{port}/analytics_dashboard.html")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Serve PRIDE MCP Analytics Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve on (default: 8080)")
    
    args = parser.parse_args()
    serve_analytics_dashboard(args.port) 