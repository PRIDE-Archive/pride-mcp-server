"""
FastAPI web server for the MCP client tools.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pathlib import Path

from .client import MCPClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="MCP Client Tools Web UI", version="0.1.0")

# Global client instance
mcp_client: Optional[MCPClient] = None

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Client Tools - PRIDE Archive</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .result-box { max-height: 400px; overflow-y: auto; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="max-w-4xl mx-auto">
            <!-- Header -->
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold text-gray-800 mb-2">🧬 MCP Client Tools</h1>
                <p class="text-gray-600">PRIDE Archive Proteomics Data Explorer</p>
                <div class="mt-4 p-4 bg-blue-50 rounded-lg">
                    <p class="text-sm text-blue-800">
                        <strong>Server URL:</strong> <span id="server-url">Loading...</span>
                    </p>
                    <p class="text-sm text-blue-800">
                        <strong>Status:</strong> <span id="server-status">Checking...</span>
                    </p>
                </div>
            </div>

            <!-- Tool Selection -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 class="text-2xl font-semibold mb-4">🔧 Available Tools</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button onclick="testTool('get_pride_facets')" 
                            class="p-4 border rounded-lg hover:bg-blue-50 transition-colors">
                        <h3 class="font-semibold">📋 Get PRIDE Facets</h3>
                        <p class="text-sm text-gray-600">Get available filter values</p>
                    </button>
                    <button onclick="testTool('search_pride_projects')" 
                            class="p-4 border rounded-lg hover:bg-blue-50 transition-colors">
                        <h3 class="font-semibold">🔍 Search Projects</h3>
                        <p class="text-sm text-gray-600">Search for proteomics projects</p>
                    </button>
                </div>
            </div>

            <!-- Search Form -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 class="text-2xl font-semibold mb-4">🔍 Search Projects</h2>
                <form id="search-form" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Keyword</label>
                        <input type="text" id="keyword" name="keyword" 
                               placeholder="e.g., cancer, proteomics, mouse"
                               class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Filters (optional)</label>
                        <textarea id="filters" name="filters" rows="3"
                                  placeholder="e.g., organisms==Homo sapiens (human),diseases==Breast cancer"
                                  class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"></textarea>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Page Size</label>
                            <input type="number" id="page_size" name="page_size" value="25" min="1" max="100"
                                   class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Page</label>
                            <input type="number" id="page" name="page" value="0" min="0"
                                   class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>
                    </div>
                    <button type="submit" 
                            class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors">
                        🔍 Search Projects
                    </button>
                </form>
            </div>

            <!-- Results -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-2xl font-semibold mb-4">📊 Results</h2>
                <div id="results" class="result-box">
                    <p class="text-gray-500 text-center py-8">No results yet. Try a search or test a tool above.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            checkServerStatus();
            setupEventListeners();
        });

        function setupEventListeners() {
            document.getElementById('search-form').addEventListener('submit', function(e) {
                e.preventDefault();
                searchProjects();
            });
        }

        async function checkServerStatus() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                document.getElementById('server-url').textContent = data.server_url || 'Unknown';
                document.getElementById('server-status').textContent = data.status || 'Unknown';
            } catch (error) {
                document.getElementById('server-status').textContent = 'Error';
                console.error('Error checking server status:', error);
            }
        }

        async function testTool(toolName) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="text-center py-4"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div><p class="mt-2">Testing tool...</p></div>';

            try {
                const response = await fetch(`/api/test-tool/${toolName}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });

                const result = await response.json();
                displayResults(toolName, result);
            } catch (error) {
                displayError(`Error testing ${toolName}: ${error.message}`);
            }
        }

        async function searchProjects() {
            const formData = new FormData(document.getElementById('search-form'));
            const params = {
                keyword: formData.get('keyword'),
                filters: formData.get('filters'),
                page_size: parseInt(formData.get('page_size')),
                page: parseInt(formData.get('page'))
            };

            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="text-center py-4"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div><p class="mt-2">Searching...</p></div>';

            try {
                const response = await fetch('/api/search-projects', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(params)
                });

                const result = await response.json();
                displayResults('search_pride_projects', result);
            } catch (error) {
                displayError(`Error searching projects: ${error.message}`);
            }
        }

        function displayResults(toolName, result) {
            const resultsDiv = document.getElementById('results');
            
            if (result.error) {
                displayError(result.error);
                return;
            }

            let html = `
                <div class="mb-4">
                    <h3 class="text-lg font-semibold text-green-600 mb-2">✅ ${toolName} - Success</h3>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <pre class="text-sm overflow-x-auto">${JSON.stringify(result, null, 2)}</pre>
                    </div>
                </div>
            `;

            resultsDiv.innerHTML = html;
        }

        function displayError(error) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="mb-4">
                    <h3 class="text-lg font-semibold text-red-600 mb-2">❌ Error</h3>
                    <div class="bg-red-50 p-4 rounded-lg">
                        <p class="text-red-800">${error}</p>
                    </div>
                </div>
            `;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface."""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    global mcp_client
    return {
        "status": "healthy" if mcp_client else "no_client",
        "server_url": mcp_client.mcp_server_url if mcp_client else None
    }

@app.post("/api/test-tool/{tool_name}")
async def test_tool(tool_name: str, request: Request):
    """Test a specific tool."""
    global mcp_client
    if not mcp_client:
        raise HTTPException(status_code=500, detail="MCP client not initialized")
    
    try:
        body = await request.json()
        result = mcp_client.call_tool(tool_name, body)
        return result
    except Exception as e:
        logger.error(f"Error testing tool {tool_name}: {e}")
        return {"error": str(e)}

@app.post("/api/search-projects")
async def search_projects(request: Request):
    """Search for projects."""
    global mcp_client
    if not mcp_client:
        raise HTTPException(status_code=500, detail="MCP client not initialized")
    
    try:
        body = await request.json()
        result = mcp_client.call_tool("search_pride_projects", body)
        return result
    except Exception as e:
        logger.error(f"Error searching projects: {e}")
        return {"error": str(e)}

def create_web_server(mcp_server_url: str, port: int = 9090):
    """Create and configure the web server."""
    global mcp_client
    
    # Initialize MCP client
    mcp_client = MCPClient(mcp_server_url)
    logger.info(f"Initialized MCP client for server: {mcp_server_url}")
    
    return app

def run_web_server(mcp_server_url: str, port: int = 9090, host: str = "127.0.0.1"):
    """Run the web server."""
    app = create_web_server(mcp_server_url, port)
    
    logger.info(f"Starting web server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Client Tools Web Server")
    parser.add_argument("--server-url", default="http://127.0.0.1:9000", 
                       help="MCP server URL")
    parser.add_argument("--port", type=int, default=9090, 
                       help="Web server port")
    parser.add_argument("--host", default="127.0.0.1", 
                       help="Web server host")
    
    args = parser.parse_args()
    
    run_web_server(args.server_url, args.port, args.host) 