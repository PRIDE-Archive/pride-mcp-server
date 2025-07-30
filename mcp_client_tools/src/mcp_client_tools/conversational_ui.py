"""
Conversational Web UI for MCP Client Tools.
This provides a chat interface where users can ask natural language questions
and the AI intelligently uses the MCP tools to answer them.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pathlib import Path

from .client import MCPClient
from .tools import PRIDE_EBI_TOOLS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="MCP Conversational UI", version="0.1.0")

# Global client instance
mcp_client: Optional[MCPClient] = None

# HTML template for the conversational interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Conversational UI - PRIDE Archive</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .chat-container { height: calc(100vh - 200px); }
        .message { max-width: 80%; }
        .user-message { background-color: #3b82f6; color: white; }
        .assistant-message { background-color: #f3f4f6; color: #1f2937; }
        .tool-call { background-color: #fef3c7; border-left: 4px solid #f59e0b; }
        .typing-indicator { display: none; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-6">
        <div class="max-w-4xl mx-auto">
            <!-- Header -->
            <div class="text-center mb-6">
                <h1 class="text-3xl font-bold text-gray-800 mb-2">🧬 MCP Conversational UI</h1>
                <p class="text-gray-600">Ask natural language questions about PRIDE Archive proteomics data</p>
                <div class="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p class="text-sm text-blue-800">
                        <strong>Server:</strong> <span id="server-status">Connecting...</span>
                    </p>
                </div>
            </div>

            <!-- Chat Interface -->
            <div class="bg-white rounded-lg shadow-lg overflow-hidden">
                <!-- Chat Messages -->
                <div id="chat-messages" class="chat-container overflow-y-auto p-4 space-y-4">
                    <div class="assistant-message message p-3 rounded-lg">
                        <p>👋 Hello! I'm your AI assistant for PRIDE Archive proteomics data. Ask me anything like:</p>
                        <ul class="mt-2 text-sm space-y-1">
                            <li>• "Find human breast cancer proteomics studies"</li>
                            <li>• "Show me mouse SWATH MS experiments"</li>
                            <li>• "What organisms are available in PRIDE?"</li>
                            <li>• "Search for Alzheimer's disease datasets"</li>
                        </ul>
                    </div>
                </div>

                <!-- Typing Indicator -->
                <div id="typing-indicator" class="typing-indicator p-4 border-t">
                    <div class="flex items-center space-x-2">
                        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        <span class="text-gray-600">AI is thinking...</span>
                    </div>
                </div>

                <!-- Input Form -->
                <div class="border-t p-4">
                    <form id="chat-form" class="flex space-x-2">
                        <input type="text" id="message-input" 
                               placeholder="Ask about proteomics data..."
                               class="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                               autocomplete="off">
                        <button type="submit" 
                                class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                            Send
                        </button>
                    </form>
                </div>
            </div>

            <!-- Example Questions -->
            <div class="mt-6 bg-white rounded-lg shadow p-4">
                <h3 class="font-semibold text-gray-800 mb-3">💡 Example Questions:</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                    <button onclick="askQuestion('Find human breast cancer proteomics studies from 2023')" 
                            class="text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
                        🔬 Find human breast cancer proteomics studies from 2023
                    </button>
                    <button onclick="askQuestion('Show me mouse SWATH MS experiments on cancer')" 
                            class="text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
                        🐭 Show me mouse SWATH MS experiments on cancer
                    </button>
                    <button onclick="askQuestion('What organisms are available in PRIDE Archive?')" 
                            class="text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
                        🧬 What organisms are available in PRIDE Archive?
                    </button>
                    <button onclick="askQuestion('Search for Alzheimer disease datasets')" 
                            class="text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
                        🧠 Search for Alzheimer disease datasets
                    </button>
                    <button onclick="askQuestion('Find studies from 2024 using MaxQuant software')" 
                            class="text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
                        📅 Find studies from 2024 using MaxQuant software
                    </button>
                    <button onclick="askQuestion('Show me recent proteomics studies from 2023-2024')" 
                            class="text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
                        🆕 Show me recent proteomics studies from 2023-2024
                    </button>
                    <button onclick="askQuestion('What software tools are commonly used in PRIDE studies?')" 
                            class="text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
                        🛠️ What software tools are commonly used in PRIDE studies?
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        const chatMessages = document.getElementById('chat-messages');
        const messageInput = document.getElementById('message-input');
        const chatForm = document.getElementById('chat-form');
        const typingIndicator = document.getElementById('typing-indicator');

        // Initialize WebSocket connection
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                document.getElementById('server-status').textContent = 'Connected';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                document.getElementById('server-status').textContent = 'Disconnected';
                // Try to reconnect after 3 seconds
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                document.getElementById('server-status').textContent = 'Error';
            };
        }

        function handleMessage(data) {
            hideTypingIndicator();
            
            if (data.type === 'tool_call') {
                addToolCallMessage(data);
            } else if (data.type === 'assistant') {
                addAssistantMessage(data.content);
            } else if (data.type === 'error') {
                addErrorMessage(data.error);
            }
        }

        function addUserMessage(content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'user-message message p-3 rounded-lg ml-auto';
            messageDiv.innerHTML = `<p>${escapeHtml(content)}</p>`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function addAssistantMessage(content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'assistant-message message p-3 rounded-lg';
            messageDiv.innerHTML = `<p>${escapeHtml(content)}</p>`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function addToolCallMessage(data) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'tool-call message p-3 rounded-lg';
            messageDiv.innerHTML = `
                <div class="flex items-center space-x-2 mb-2">
                    <span class="text-orange-600">🔧</span>
                    <span class="font-semibold text-sm">Tool Call: ${data.tool}</span>
                </div>
                <div class="text-sm">
                    <p><strong>Parameters:</strong></p>
                    <pre class="bg-white p-2 rounded text-xs overflow-x-auto">${JSON.stringify(data.parameters, null, 2)}</pre>
                    ${data.result ? `<p class="mt-2"><strong>Result:</strong></p><pre class="bg-white p-2 rounded text-xs overflow-x-auto">${JSON.stringify(data.result, null, 2)}</pre>` : ''}
                </div>
            `;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function addErrorMessage(error) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'bg-red-100 border-l-4 border-red-500 text-red-700 p-3 rounded-lg';
            messageDiv.innerHTML = `<p><strong>Error:</strong> ${escapeHtml(error)}</p>`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function showTypingIndicator() {
            typingIndicator.style.display = 'block';
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function hideTypingIndicator() {
            typingIndicator.style.display = 'none';
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function askQuestion(question) {
            messageInput.value = question;
            chatForm.dispatchEvent(new Event('submit'));
        }

        // Event listeners
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (!message) return;

            addUserMessage(message);
            messageInput.value = '';
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                showTypingIndicator();
                ws.send(JSON.stringify({
                    type: 'user_message',
                    content: message
                }));
            } else {
                addErrorMessage('WebSocket not connected. Please refresh the page.');
            }
        });

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            connectWebSocket();
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the conversational web interface."""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    global mcp_client
    return {
        "status": "healthy" if mcp_client else "no_client",
        "server_url": mcp_client.mcp_server_url if mcp_client else None
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "user_message":
                await handle_user_message(websocket, message_data["content"])
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))

async def handle_user_message(websocket: WebSocket, user_message: str):
    """Handle user message and generate AI response using MCP tools."""
    global mcp_client
    
    if not mcp_client:
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": "MCP client not initialized"
        }))
        return
    
    try:
        # Step 1: Get available facets to understand what's available
        await websocket.send_text(json.dumps({
            "type": "tool_call",
            "tool": "get_pride_facets",
            "parameters": {},
            "result": None
        }))
        
        facets_result = mcp_client.call_tool("get_pride_facets", {})
        
        await websocket.send_text(json.dumps({
            "type": "tool_call",
            "tool": "get_pride_facets",
            "parameters": {},
            "result": facets_result
        }))
        
        # Step 2: Analyze the user question and determine search parameters
        # This is where you would integrate with an AI service to understand the intent
        search_params = analyze_user_question(user_message, facets_result)
        
        # Step 3: Execute the search
        if search_params:
            await websocket.send_text(json.dumps({
                "type": "tool_call",
                "tool": "search_pride_projects",
                "parameters": search_params,
                "result": None
            }))
            
            search_result = mcp_client.call_tool("search_pride_projects", search_params)
            
            await websocket.send_text(json.dumps({
                "type": "tool_call",
                "tool": "search_pride_projects",
                "parameters": search_params,
                "result": search_result
            }))
            
            # Step 4: Generate natural language response
            response = generate_response(user_message, search_result, facets_result)
        else:
            response = "I couldn't understand your question. Please try asking about proteomics data, organisms, diseases, or experimental techniques."
        
        await websocket.send_text(json.dumps({
            "type": "assistant",
            "content": response
        }))
        
    except Exception as e:
        logger.error(f"Error handling user message: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))

def analyze_user_question(question: str, facets_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Analyze user question and extract search parameters."""
    question_lower = question.lower()
    
    # Extract keywords
    keywords = []
    if "cancer" in question_lower:
        keywords.append("cancer")
    if "proteomics" in question_lower:
        keywords.append("proteomics")
    if "alzheimer" in question_lower:
        keywords.append("alzheimer")
    if "breast" in question_lower:
        keywords.append("breast")
    
    # Extract organism information
    organisms = []
    if "human" in question_lower:
        organisms.append("Homo sapiens (human)")
    if "mouse" in question_lower:
        organisms.append("Mus musculus (mouse)")
    if "yeast" in question_lower:
        organisms.append("Saccharomyces cerevisiae (baker's yeast)")
    
    # Extract experimental techniques
    experiment_types = []
    if "swath" in question_lower:
        experiment_types.append("SWATH MS")
    if "tmt" in question_lower:
        experiment_types.append("TMT")
    
    # Extract diseases
    diseases = []
    if "breast cancer" in question_lower:
        diseases.append("Breast cancer")
    if "alzheimer" in question_lower:
        diseases.append("Alzheimer's disease")
    
    # Build search parameters
    search_params = {
        "keyword": " ".join(keywords) if keywords else "proteomics"
    }
    
    facets = []
    if organisms:
        facets.append({"name": "organism", "values": organisms})
    if experiment_types:
        facets.append({"name": "experiment_type", "values": experiment_types})
    if diseases:
        facets.append({"name": "disease", "values": diseases})
    
    if facets:
        search_params["facets"] = facets
    
    return search_params

def generate_response(user_question: str, search_result: Dict[str, Any], facets_data: Dict[str, Any]) -> str:
    """Generate a natural language response based on search results."""
    
    if "error" in search_result:
        return f"I encountered an error while searching: {search_result['error']}"
    
    # Extract project count
    projects = search_result.get("data", [])
    project_count = len(projects)
    
    if project_count == 0:
        return f"I searched for '{user_question}' but found no matching projects. Try broadening your search or using different keywords."
    
    # Generate response
    response = f"I found {project_count} project(s) matching your query about '{user_question}'. "
    
    if project_count <= 5:
        response += "Here are the projects:\n\n"
        for i, project in enumerate(projects[:5], 1):
            response += f"{i}. **{project.get('accession', 'Unknown')}**: {project.get('title', 'No title')}\n"
    else:
        response += f"Here are the first 5 projects:\n\n"
        for i, project in enumerate(projects[:5], 1):
            response += f"{i}. **{project.get('accession', 'Unknown')}**: {project.get('title', 'No title')}\n"
        response += f"\n... and {project_count - 5} more projects."
    
    response += "\n\nYou can ask me to get more details about any specific project by mentioning its accession number."
    
    return response

def create_conversational_ui(mcp_server_url: str, port: int = 9090):
    """Create and configure the conversational web UI."""
    global mcp_client
    
    # Initialize MCP client
    mcp_client = MCPClient(mcp_server_url)
    logger.info(f"Initialized MCP client for server: {mcp_server_url}")
    
    return app

def run_conversational_ui(mcp_server_url: str, port: int = 9090, host: str = "127.0.0.1"):
    """Run the conversational web UI."""
    app = create_conversational_ui(mcp_server_url, port)
    
    logger.info(f"Starting conversational UI on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Conversational UI")
    parser.add_argument("--server-url", default="http://127.0.0.1:9000", 
                       help="MCP server URL")
    parser.add_argument("--port", type=int, default=9090, 
                       help="Web server port")
    parser.add_argument("--host", default="127.0.0.1", 
                       help="Web server host")
    
    args = parser.parse_args()
    
    run_conversational_ui(args.server_url, args.port, args.host) 