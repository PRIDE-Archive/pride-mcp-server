#!/usr/bin/env python3
"""
Secure HTTP server to serve the analytics dashboard.
Only serves the analytics dashboard HTML file and blocks access to other files.
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

class SecureAnalyticsHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler that only serves the analytics dashboard."""
    
    def do_GET(self):
        """Handle GET requests - only allow access to analytics dashboard."""
        # Normalize the path
        path = self.path.split('?')[0]  # Remove query parameters
        
        # Allow access to analytics dashboard and its assets
        allowed_paths = [
            '/',
            '/analytics/',
            '/analytics_dashboard.html',
            '/favicon.ico'
        ]
        
        # Check if the path is allowed
        if path in allowed_paths:
            if path in ['/', '/analytics/']:
                # Redirect root and analytics paths to the dashboard
                self.path = '/analytics_dashboard.html'
            super().do_GET()
        else:
            # Block access to all other files
            self.send_error(403, "Forbidden - Access denied")
            return
    
    def log_message(self, format, *args):
        """Custom logging to show access attempts."""
        # Log all access attempts for security monitoring
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}")

def serve_analytics_dashboard(port=8080):
    """Serve the analytics dashboard on the specified port."""
    
    # Change to the directory containing the HTML file
    os.chdir(Path(__file__).parent)
    
    # Create a secure HTTP server with custom handler
    handler = SecureAnalyticsHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 Secure Analytics Dashboard Server")
        print(f"   URL: http://localhost:{port}/analytics_dashboard.html")
        print(f"   Security: Only analytics dashboard access allowed")
        print(f"   Press Ctrl+C to stop")
        
        # Open the dashboard in the default browser
        webbrowser.open(f"http://localhost:{port}/analytics_dashboard.html")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Serve PRIDE MCP Analytics Dashboard (Secure)")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve on (default: 8080)")
    
    args = parser.parse_args()
    serve_analytics_dashboard(args.port) 