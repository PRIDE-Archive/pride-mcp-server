"""
Professional UI Components for MCP Client Tools.
Modern, clean design system for scientific applications.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Load environment variables from config.env
def load_env_config():
    """Load environment variables from config.env file."""
    # Look for config.env in the parent directory (project root)
    config_file = Path("../config.env")
    if not config_file.exists():
        # Also try current directory
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

# Load environment variables
load_env_config()

try:
    from .client import MCPClient
except ImportError:
    from mcp_client_tools.client import MCPClient
try:
    from .tools import PRIDE_EBI_TOOLS
except ImportError:
    from mcp_client_tools.tools import PRIDE_EBI_TOOLS

try:
    from .ai_conversational_ui import AIService
except ImportError:
    from mcp_client_tools.ai_conversational_ui import AIService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="PRIDE Archive Professional UI", version="2.0.0")

# Global client instance
mcp_client: Optional[MCPClient] = None

# Initialize AI service
try:
    ai_service = AIService()
    logger.info("✅ AI service initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize AI service: {e}")
    ai_service = None

# Professional HTML template with modern design
PROFESSIONAL_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PRIDE Archive - Professional Research Interface</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="icon" type="image/png" href="https://www.ebi.ac.uk/pride/archive/logo/PRIDE_logo_Archive.png">
    <style>
        :root {
            --primary-50: #eff6ff;
            --primary-100: #dbeafe;
            --primary-200: #bfdbfe;
            --primary-300: #93c5fd;
            --primary-400: #60a5fa;
            --primary-500: #3b82f6;
            --primary-600: #2563eb;
            --primary-700: #1d4ed8;
            --primary-800: #1e40af;
            --primary-900: #1e3a8a;
            --primary-950: #172554;
            
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-400: #9ca3af;
            --gray-500: #6b7280;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-800: #1f2937;
            --gray-900: #111827;
            --gray-950: #030712;
            
            --success-50: #f0fdf4;
            --success-500: #22c55e;
            --success-600: #16a34a;
            
            --warning-50: #fffbeb;
            --warning-500: #f59e0b;
            --warning-600: #d97706;
            
            --error-50: #fef2f2;
            --error-500: #ef4444;
            --error-600: #dc2626;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--gray-50) 0%, var(--primary-50) 50%, var(--gray-100) 100%);
            min-height: 100vh;
            color: var(--gray-900);
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-800) 100%);
            color: white;
            padding: 2rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .header-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .logo-icon {
            width: 48px;
            height: 48px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        
        .title-section h1 {
            font-size: 1.875rem;
            font-weight: 800;
            margin: 0;
            line-height: 1.2;
        }
        
        .title-section p {
            font-size: 1rem;
            opacity: 0.9;
            margin: 0.25rem 0 0 0;
        }
        
        .status-badge {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .main-content {
            padding: 2rem 0;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
            border: 1px solid var(--gray-200);
            overflow: hidden;
        }
        
        .card-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--gray-200);
            background: var(--gray-50);
        }
        
        .card-body {
            padding: 1.5rem;
        }
        
        .chat-container {
            height: 500px;
            overflow-y: auto;
            padding: 1rem;
            background: var(--gray-50);
        }
        
        .message {
            margin-bottom: 1rem;
            max-width: 80%;
        }
        
        .message.user {
            margin-left: auto;
        }
        
        .message.assistant {
            margin-right: auto;
        }
        
        .message-content {
            padding: 1rem;
            border-radius: 12px;
            position: relative;
        }
        
        .message.user .message-content {
            background: var(--primary-600);
            color: white;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
        }
        
        .message.assistant .message-content {
            background: white;
            border: 1px solid var(--gray-200);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .message-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
            font-weight: 600;
        }
        
        .message.user .message-header {
            color: rgba(255, 255, 255, 0.9);
        }
        
        .message.assistant .message-header {
            color: var(--gray-600);
        }
        
        .avatar {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
        }
        
        .message.user .avatar {
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }
        
        .message.assistant .avatar {
            background: var(--primary-100);
            color: var(--primary-700);
        }
        
        .input-section {
            padding: 1.5rem;
            border-top: 1px solid var(--gray-200);
            background: white;
        }
        
        .input-form {
            display: flex;
            gap: 1rem;
            align-items: flex-end;
        }
        
        .input-group {
            flex: 1;
        }
        
        .input-label {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--gray-700);
            margin-bottom: 0.5rem;
        }
        
        .input-field {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1px solid var(--gray-300);
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.2s ease;
        }
        
        .input-field:focus {
            outline: none;
            border-color: var(--primary-500);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-primary {
            background: var(--primary-600);
            color: white;
        }
        
        .btn-primary:hover {
            background: var(--primary-700);
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: var(--gray-100);
            color: var(--gray-700);
            border: 1px solid var(--gray-300);
        }
        
        .btn-secondary:hover {
            background: var(--gray-200);
        }
        
        .examples-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .example-card {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 1rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .example-card:hover {
            border-color: var(--primary-300);
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
            transform: translateY(-2px);
        }
        
        .example-icon {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
        
        .example-title {
            font-weight: 600;
            color: var(--gray-900);
            margin-bottom: 0.25rem;
        }
        
        .example-description {
            font-size: 0.875rem;
            color: var(--gray-600);
        }
        
        .typing-indicator {
            display: none;
            padding: 1rem;
            background: var(--gray-50);
            border-top: 1px solid var(--gray-200);
        }
        
        .typing-dots {
            display: flex;
            gap: 0.25rem;
            align-items: center;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            background: var(--primary-500);
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
        
        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 0.5rem;
        }
        
        .status-connected { background: var(--success-500); }
        .status-disconnected { background: var(--error-500); }
        .status-connecting { background: var(--warning-500); }
        
        /* Markdown content styles */
        .prose {
            color: var(--gray-900);
            line-height: 1.6;
        }
        
        .prose h1, .prose h2, .prose h3, .prose h4, .prose h5, .prose h6 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
            color: var(--gray-900);
        }
        
        .prose h1 { font-size: 1.5em; }
        .prose h2 { font-size: 1.3em; }
        .prose h3 { font-size: 1.1em; }
        
        .prose p {
            margin-bottom: 1em;
        }
        
        .prose ul, .prose ol {
            margin-bottom: 1em;
            padding-left: 1.5em;
        }
        
        .prose li {
            margin-bottom: 0.5em;
        }
        
        .prose strong {
            font-weight: 600;
            color: var(--gray-900);
        }
        
        .prose em {
            font-style: italic;
        }
        
        .prose a {
            color: var(--primary-600);
            text-decoration: underline;
            transition: color 0.2s;
        }
        
        .prose a:hover {
            color: var(--primary-700);
        }
        
        .prose code {
            background-color: var(--gray-100);
            padding: 0.2em 0.4em;
            border-radius: 0.25em;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: var(--gray-900);
        }
        
        .prose pre {
            background-color: var(--gray-100);
            padding: 1em;
            border-radius: 0.5em;
            overflow-x: auto;
            margin-bottom: 1em;
            border-left: 4px solid var(--primary-600);
        }
        
        /* Notification styles */
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--primary-600);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                text-align: center;
            }
            
            .input-form {
                flex-direction: column;
            }
            
            .examples-grid {
                grid-template-columns: 1fr;
            }
            
            .message {
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo-icon">🧬</div>
                    <div class="title-section">
                        <h1>PRIDE Archive</h1>
                        <p>Professional Research Interface</p>
                        <div class="mt-2 flex items-center space-x-2">
                            <span class="text-xs bg-white/20 px-2 py-1 rounded-full">Powered by</span>
                            <span class="text-xs font-semibold bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-2 py-1 rounded-full">Gemini AI</span>
                        </div>
                    </div>
                </div>
                <div class="status-badge">
                    <span class="status-indicator status-connecting" id="status-indicator"></span>
                    <span id="status-text">Connecting...</span>
                </div>
            </div>
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            <div class="card">
                <div class="card-header">
                    <h2 class="text-xl font-semibold text-gray-900">AI Research Assistant</h2>
                    <p class="text-gray-600 mt-1">Ask natural language questions about proteomics data</p>
                </div>
                
                <div class="chat-container" id="chat-container">
                    <div class="message assistant">
                        <div class="message-content">
                            <div class="message-header">
                                <div class="avatar">AI</div>
                                <span>Research Assistant</span>
                            </div>
                            <div class="message-text">
                                <p>Welcome to the PRIDE Archive Research Interface! I'm powered by <strong>Gemini AI</strong> and here to help you explore proteomics data with natural language queries.</p>
                                <p class="mt-2">Try asking about:</p>
                                <ul class="mt-2 space-y-1">
                                    <li>• Specific organisms or diseases</li>
                                    <li>• Experimental techniques (SWATH, TMT, etc.)</li>
                                    <li>• Research topics or keywords</li>
                                    <li>• Date ranges or software tools</li>
                                </ul>
                                <p class="mt-3 text-sm text-gray-600">💡 <strong>Tip:</strong> Click on any integration guide below to see step-by-step instructions for connecting to your favorite AI tools!</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="typing-indicator" id="typing-indicator">
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <span class="ml-2 text-gray-600">AI is thinking...</span>
                    </div>
                </div>
                
                <div class="input-section">
                    <form id="chat-form" class="input-form">
                        <div class="input-group">
                            <label class="input-label" for="message-input">Your Question</label>
                            <input type="text" id="message-input" class="input-field" 
                                   placeholder="e.g., Find human breast cancer proteomics studies from 2023..."
                                   autocomplete="off">
                        </div>
                        <button type="submit" class="btn btn-primary">
                            <span>Send</span>
                            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                            </svg>
                        </button>
                    </form>
                </div>
            </div>
            
            <div class="card mt-6">
                <div class="card-header">
                    <h3 class="text-lg font-semibold text-gray-900">Quick Examples</h3>
                    <p class="text-gray-600 mt-1">Click any example to get started</p>
                </div>
                <div class="card-body">
                    <div class="examples-grid">
                        <div class="example-card" data-question="What organisms are available in PRIDE Archive?">
                            <div class="example-icon">🧬</div>
                            <div class="example-title">Available Organisms</div>
                            <div class="example-description">Explore the diversity of species in the database</div>
                        </div>
                        <div class="example-card" data-question="Find human breast cancer proteomics studies">
                            <div class="example-icon">🔬</div>
                            <div class="example-title">Cancer Research</div>
                            <div class="example-description">Search for human breast cancer studies</div>
                        </div>
                        <div class="example-card" data-question="Show me mouse proteomics experiments on cancer">
                            <div class="example-icon">🐭</div>
                            <div class="example-title">Mouse Studies</div>
                            <div class="example-description">Find mouse cancer proteomics experiments</div>
                        </div>
                        <div class="example-card" data-question="Search for Alzheimer disease datasets">
                            <div class="example-icon">🧠</div>
                            <div class="example-title">Neurological Research</div>
                            <div class="example-description">Explore Alzheimer's disease datasets</div>
                        </div>
                        <div class="example-card" data-question="Find studies from 2024 using MaxQuant software">
                            <div class="example-icon">📅</div>
                            <div class="example-title">Recent Studies</div>
                            <div class="example-description">2024 studies with MaxQuant analysis</div>
                        </div>
                        <div class="example-card" data-question="What software tools are commonly used in PRIDE studies?">
                            <div class="example-icon">🛠️</div>
                            <div class="example-title">Software Tools</div>
                            <div class="example-description">Discover popular analysis tools</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Available Tools Section -->
            <div class="card mt-6">
                <div class="card-header">
                    <h3 class="text-lg font-semibold text-gray-900">🛠️ Available MCP Tools</h3>
                    <p class="text-gray-600 mt-1">Direct access to PRIDE Archive functionality</p>
                </div>
                <div class="card-body">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="p-4 border border-gray-200 rounded-lg">
                            <h4 class="font-semibold text-gray-900 mb-2">📋 get_pride_facets</h4>
                            <p class="text-sm text-gray-600 mb-2">Get available filter values from PRIDE Archive</p>
                            <div class="text-xs text-gray-500">
                                <strong>Parameters:</strong> facet_page_size, facet_page, keyword
                            </div>
                        </div>
                        <div class="p-4 border border-gray-200 rounded-lg">
                            <h4 class="font-semibold text-gray-900 mb-2">🔍 fetch_projects</h4>
                            <p class="text-sm text-gray-600 mb-2">Search for proteomics projects</p>
                            <div class="text-xs text-gray-500">
                                <strong>Parameters:</strong> keyword, filters, page_size, page, sort_direction, sort_fields
                            </div>
                        </div>
                        <div class="p-4 border border-gray-200 rounded-lg">
                            <h4 class="font-semibold text-gray-900 mb-2">📄 get_project_details</h4>
                            <p class="text-sm text-gray-600 mb-2">Get detailed information about a specific project</p>
                            <div class="text-xs text-gray-500">
                                <strong>Parameters:</strong> project_accession
                            </div>
                        </div>
                        <div class="p-4 border border-gray-200 rounded-lg">
                            <h4 class="font-semibold text-gray-900 mb-2">📁 get_project_files</h4>
                            <p class="text-sm text-gray-600 mb-2">Get file information for a project</p>
                            <div class="text-xs text-gray-500">
                                <strong>Parameters:</strong> project_accession, file_type
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Integration Guides Section -->
            <div class="card mt-6">
                <div class="card-header">
                    <h3 class="text-lg font-semibold text-gray-900">🔗 Integration Guides</h3>
                    <p class="text-gray-600 mt-1">Connect PRIDE Archive MCP Server to your favorite AI tools</p>
                </div>
                <div class="card-body">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div class="integration-card" data-tool="claude">
                            <div class="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all cursor-pointer">
                                <div class="w-10 h-10 bg-gradient-to-br from-orange-400 to-red-500 rounded-lg flex items-center justify-center text-white font-bold">
                                    C
                                </div>
                                <div>
                                    <h4 class="font-semibold text-gray-900">Claude Desktop</h4>
                                    <p class="text-sm text-gray-600">Settings → Extensions</p>
                                </div>
                            </div>
                        </div>
                        <div class="integration-card" data-tool="cursor">
                            <div class="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all cursor-pointer">
                                <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold">
                                    C
                                </div>
                                <div>
                                    <h4 class="font-semibold text-gray-900">Cursor IDE</h4>
                                    <p class="text-sm text-gray-600">Settings → MCP</p>
                                </div>
                            </div>
                        </div>
                        <div class="integration-card" data-tool="chatgpt">
                            <div class="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all cursor-pointer">
                                <div class="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center text-white font-bold">
                                    G
                                </div>
                                <div>
                                    <h4 class="font-semibold text-gray-900">ChatGPT</h4>
                                    <p class="text-sm text-gray-600">With MCP Plugin</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Server Information Section -->
            <div class="card mt-6">
                <div class="card-header">
                    <h3 class="text-lg font-semibold text-gray-900">📋 Server Information</h3>
                    <p class="text-gray-600 mt-1">MCP Server configuration details</p>
                </div>
                <div class="card-body">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="p-3 bg-gray-50 rounded-lg">
                            <div class="text-sm font-medium text-gray-700">Server URL</div>
                            <div class="text-sm text-gray-900 font-mono">{{ mcp_server_url }}</div>
                        </div>
                        <div class="p-3 bg-gray-50 rounded-lg">
                            <div class="text-sm font-medium text-gray-700">Server Name</div>
                            <div class="text-sm text-gray-900">PRIDE Archive MCP Server</div>
                        </div>
                        <div class="p-3 bg-gray-50 rounded-lg">
                            <div class="text-sm font-medium text-gray-700">Description</div>
                            <div class="text-sm text-gray-900">Access proteomics data from PRIDE Archive</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        let ws = null;
        const chatContainer = document.getElementById('chat-container');
        const messageInput = document.getElementById('message-input');
        const chatForm = document.getElementById('chat-form');
        const typingIndicator = document.getElementById('typing-indicator');
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        let currentProgressStep = null;

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            
            // Check if we're running through ingress (has /pride/services/pride-mcp in path)
            const isIngress = window.location.pathname.includes('/pride/services/pride-mcp');
            
            // Use appropriate WebSocket path
            const wsPath = isIngress ? '/pride/services/pride-mcp/ui/ws' : '/ws';
            const wsUrl = protocol + '//' + window.location.host + wsPath;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                statusText.textContent = 'Connected';
                statusIndicator.className = 'status-indicator status-connected';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = function() {
                statusText.textContent = 'Disconnected';
                statusIndicator.className = 'status-indicator status-disconnected';
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onerror = function(error) {
                statusText.textContent = 'Error';
                statusIndicator.className = 'status-indicator status-disconnected';
            };
        }

        function handleMessage(data) {
            hideTypingIndicator();
            
            if (data.type === 'assistant') {
                // Remove progress step when complete
                if (currentProgressStep) {
                    currentProgressStep.remove();
                    currentProgressStep = null;
                }
                addAssistantMessage(data.content);
            } else if (data.type === 'error') {
                // Remove progress step on error
                if (currentProgressStep) {
                    currentProgressStep.remove();
                    currentProgressStep = null;
                }
                addErrorMessage(data.error);
            } else if (data.type === 'progress') {
                // Handle dynamic progress updates
                if (!currentProgressStep) {
                    currentProgressStep = showProgressStep(data.step || 'Processing', data.message || 'Working...');
                } else {
                    updateProgressStep(currentProgressStep, data.step || 'Processing', data.message || 'Working...');
                }
            }
        }

        function showProgressStep(step, message) {
            const progressDiv = document.createElement('div');
            progressDiv.className = 'message assistant progress-message';
            progressDiv.innerHTML = `
                <div class="message-content" style="background: var(--primary-50); border-color: var(--primary-200);">
                    <div class="message-header">
                        <div class="avatar" style="background: var(--primary-100); color: var(--primary-700);">⚡</div>
                        <span>Processing</span>
                    </div>
                    <div class="message-text" style="color: var(--primary-700);">
                        <div class="flex items-center space-x-2 mb-2">
                            <span class="font-semibold">${step}</span>
                            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-500"></div>
                        </div>
                        <p>${message}</p>
                    </div>
                </div>
            `;
            chatContainer.appendChild(progressDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return progressDiv;
        }

        function updateProgressStep(progressDiv, step, message) {
            if (progressDiv) {
                const stepText = progressDiv.querySelector('.font-semibold');
                const messageText = progressDiv.querySelector('p');
                
                if (stepText) stepText.textContent = step;
                if (messageText) messageText.textContent = message;
            }
        }

        function addUserMessage(content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user';
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-header">
                        <div class="avatar">You</div>
                        <span>You</span>
                    </div>
                    <div class="message-text">${escapeHtml(content)}</div>
                </div>
            `;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function addAssistantMessage(content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant';
            
            // Parse markdown content
            const parsedContent = marked.parse(content);
            
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-header">
                        <div class="avatar">AI</div>
                        <span>Research Assistant</span>
                    </div>
                    <div class="message-text prose prose-sm max-w-none">${parsedContent}</div>
                </div>
            `;
            chatContainer.appendChild(messageDiv);
            
            // Ensure smooth scrolling to the new message
            setTimeout(() => {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 50);
        }

        function addErrorMessage(error) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant';
            messageDiv.innerHTML = `
                <div class="message-content" style="background: var(--error-50); border-color: var(--error-200);">
                    <div class="message-header">
                        <div class="avatar" style="background: var(--error-100); color: var(--error-700);">⚠</div>
                        <span>Error</span>
                    </div>
                    <div class="message-text" style="color: var(--error-700);">${escapeHtml(error)}</div>
                </div>
            `;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showTypingIndicator() {
            typingIndicator.style.display = 'block';
            chatContainer.scrollTop = chatContainer.scrollHeight;
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
            
            // Scroll to chat after asking question
            setTimeout(() => {
                scrollToChat();
            }, 200);
        }

        function showIntegrationHelp(tool) {
            const helpSteps = {
                claude: [
                    "1. Open Claude Desktop",
                    "2. Go to Settings → Extensions", 
                    "3. Click 'Add Extension'",
                    "4. Select 'MCP (Model Context Protocol)'",
                    "5. Enter Server URL: http://localhost:9000",
                    "6. Enter Server Name: PRIDE Archive MCP Server",
                    "7. Click 'Add' and restart if prompted"
                ],
                cursor: [
                    "1. Open Cursor IDE",
                    "2. Go to Settings (Cmd/Ctrl + ,)",
                    "3. Search for 'MCP' or 'Model Context Protocol'",
                    "4. Add new MCP server configuration:",
                    "   - Server URL: http://localhost:9000",
                    "   - Server Name: PRIDE Archive MCP Server",
                    "5. Save and restart Cursor if needed"
                ],
                chatgpt: [
                    "1. Install the MCP plugin for ChatGPT",
                    "2. Open ChatGPT and go to Settings",
                    "3. Navigate to Plugins section",
                    "4. Add new MCP server:",
                    "   - Server URL: http://localhost:9000",
                    "   - Server Name: PRIDE Archive MCP Server",
                    "5. Save and restart ChatGPT"
                ]
            };

            const steps = helpSteps[tool] || [];
            const toolNames = {
                claude: "Claude Desktop",
                cursor: "Cursor IDE", 
                chatgpt: "ChatGPT"
            };

            let message = `## ${toolNames[tool]} Integration

`;
            message += steps.join(`
`);
            
            // Add as assistant message
            addAssistantMessage(message);
            
            // Scroll to chat and highlight the new message
            setTimeout(() => {
                scrollToChat();
                highlightLatestMessage();
            }, 400);
        }

        function highlightLatestMessage() {
            const messages = chatContainer.querySelectorAll('.message');
            const latestMessage = messages[messages.length - 1];
            
            if (latestMessage) {
                // Add highlight animation
                latestMessage.style.transition = 'all 0.3s ease';
                latestMessage.style.transform = 'scale(1.02)';
                latestMessage.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.3)';
                
                // Remove highlight after 2 seconds
                setTimeout(() => {
                    latestMessage.style.transform = 'scale(1)';
                    latestMessage.style.boxShadow = '';
                }, 2000);
            }
        }

        function showNotification(message, duration = 3000) {
            // Remove existing notification
            const existingNotification = document.querySelector('.notification');
            if (existingNotification) {
                existingNotification.remove();
            }
            
            // Create new notification
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = message;
            document.body.appendChild(notification);
            
            // Show notification
            setTimeout(() => {
                notification.classList.add('show');
            }, 100);
            
            // Hide notification
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, duration);
        }

        function scrollToChat() {
            // Scroll the chat container to the bottom
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            // Also scroll the page to make sure the chat is visible
            const chatCard = chatContainer.closest('.card');
            if (chatCard) {
                chatCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

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
                addErrorMessage('Connection lost. Please refresh the page.');
            }
        });

        document.addEventListener('DOMContentLoaded', function() {
            connectWebSocket();
            setupEventListeners();
        });

        function setupEventListeners() {
            // Setup integration help buttons
            document.querySelectorAll('.integration-card').forEach(card => {
                card.addEventListener('click', function() {
                    const tool = this.getAttribute('data-tool');
                    if (tool) {
                        // Add click feedback
                        this.style.transform = 'scale(0.95)';
                        setTimeout(() => {
                            this.style.transform = '';
                        }, 150);
                        
                        const toolNames = {
                            claude: "Claude Desktop",
                            cursor: "Cursor IDE", 
                            chatgpt: "ChatGPT"
                        };
                        
                        showNotification(`📋 Showing ${toolNames[tool]} integration guide...`);
                        showIntegrationHelp(tool);
                    }
                });
            });

            // Setup example question buttons
            document.querySelectorAll('.example-card').forEach(card => {
                card.addEventListener('click', function() {
                    const question = this.getAttribute('data-question');
                    if (question) {
                        // Add click feedback
                        this.style.transform = 'scale(0.95)';
                        setTimeout(() => {
                            this.style.transform = '';
                        }, 150);
                        
                        showNotification(`🔍 Asking: "${question.substring(0, 50)}${question.length > 50 ? '...' : ''}"`);
                        askQuestion(question);
                    }
                });
            });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the professional web interface."""
    # Get the MCP server URL from the global variable or environment
    server_url = getattr(mcp_client, 'server_url', 'http://localhost:9001') if mcp_client else 'http://localhost:9001'
    
    # Dynamically determine the display URL based on how the user is accessing the UI
    request_url = str(request.url)
    request_host = request.headers.get('host', 'localhost:9090')
    
    # Detect the access method and show appropriate MCP server URL
    if '/pride/services/pride-mcp/ui' in request_url:
        # User is accessing through ingress - show ingress MCP URL
        # Extract the base URL and replace UI path with MCP path
        base_url = request_url.replace('/pride/services/pride-mcp/ui', '')
        display_url = f"{base_url}/pride/services/pride-mcp/mcp/"
    elif 'localhost' in request_host or '127.0.0.1' in request_host:
        # User is accessing locally - show localhost MCP URL
        display_url = f"http://{request_host.replace(':9090', ':9001')}/mcp/"
    else:
        # User is accessing via NodePort - show NodePort MCP URL
        # Extract the host and port from the request
        if ':' in request_host:
            host_part = request_host.split(':')[0]
            port_part = request_host.split(':')[1]
            # Map UI port to MCP port based on current NodePort configuration
            if port_part == '9090':
                mcp_port = '31188'
            elif port_part == '31429':  # NodePort for UI
                mcp_port = '31188'      # NodePort for MCP
            elif port_part == '32378':  # NodePort for UI
                mcp_port = '31188'      # NodePort for MCP (not ingress)
            else:
                mcp_port = '31188'  # Default MCP NodePort
            display_url = f"http://{host_part}:{mcp_port}/mcp/"
        else:
            display_url = f"http://{request_host}:31188/mcp/"
    
    # Replace the template variable
    template_content = PROFESSIONAL_HTML_TEMPLATE.replace('{{ mcp_server_url }}', display_url)
    return HTMLResponse(content=template_content)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "version": "2.0.0",
        "service": "PRIDE Archive Professional UI"
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    
    try:
        while True:
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
    """Handle user message using AI to intelligently call MCP tools."""
    global mcp_client
    
    # Record start time for response time calculation
    start_time = asyncio.get_event_loop().time()
    
    if not mcp_client:
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": "MCP client not initialized"
        }))
        return
    
    try:
        # Step 1: Use AI to analyze the question and determine what tools to call
        await websocket.send_text(json.dumps({
            "type": "progress",
            "step": "AI Analysis",
            "message": "Analyzing your question and determining required tools..."
        }))
        
        # Add timeout protection for AI analysis with fallback
        ai_analysis = None
        
        # Check if AI service is available
        if ai_service is None:
            logger.warning("AI service not available, using fallback")
            # Smart fallback: determine if we need to search projects or just get facets
            user_message_lower = user_message.lower()
            if any(keyword in user_message_lower for keyword in ["organism", "available", "filter", "facet", "what can", "what are", "list", "show me what"]):
                # Questions about available data - only get facets
                ai_analysis = {
                    "intent": "get_available_data",
                    "tools_to_call": [
                        {
                            "tool_name": "get_pride_facets",
                            "parameters": {}
                        }
                    ]
                }
            else:
                # Search questions - get facets and projects
                ai_analysis = {
                    "intent": "search_projects",
                    "tools_to_call": [
                        {
                            "tool_name": "get_pride_facets",
                            "parameters": {
                                "keyword": user_message
                            }
                        },
                        {
                            "tool_name": "fetch_projects",
                            "parameters": {
                                "keyword": user_message,
                                "page_size": 25,
                                "page": 0
                            }
                        }
                    ]
                }
            await websocket.send_text(json.dumps({
                "type": "progress",
                "step": "AI Analysis",
                "message": "Using fallback analysis (AI service unavailable)..."
            }))
        else:
            try:
                # Use asyncio.wait_for to prevent infinite hanging
                ai_analysis = await asyncio.wait_for(
                    asyncio.to_thread(ai_service.analyze_question, user_message, PRIDE_EBI_TOOLS),
                    timeout=15.0  # Reduced to 15 second timeout
                )
            except asyncio.TimeoutError:
                logger.error("AI analysis timed out, using fallback")
                # Smart fallback: determine if we need to search projects or just get facets
                user_message_lower = user_message.lower()
                if any(keyword in user_message_lower for keyword in ["organism", "available", "filter", "facet", "what can", "what are", "list", "show me what"]):
                    # Questions about available data - only get facets
                    ai_analysis = {
                        "intent": "get_available_data",
                        "tools_to_call": [
                            {
                                "tool_name": "get_pride_facets",
                                "parameters": {}
                            }
                        ]
                    }
                else:
                    # Search questions - get facets and projects
                    ai_analysis = {
                        "intent": "search_projects",
                        "tools_to_call": [
                            {
                                "tool_name": "get_pride_facets",
                                "parameters": {
                                    "keyword": user_message
                                }
                            },
                            {
                                "tool_name": "fetch_projects",
                                "parameters": {
                                    "keyword": user_message,
                                    "page_size": 25,
                                    "page": 0
                                }
                            }
                        ]
                    }
                await websocket.send_text(json.dumps({
                    "type": "progress",
                    "step": "AI Analysis",
                    "message": "Using fallback analysis due to timeout..."
                }))
            except Exception as ai_error:
                logger.error(f"AI analysis failed: {ai_error}, using fallback")
                # Smart fallback: determine if we need to search projects or just get facets
                user_message_lower = user_message.lower()
                if any(keyword in user_message_lower for keyword in ["organism", "available", "filter", "facet", "what can", "what are", "list", "show me what"]):
                    # Questions about available data - only get facets
                    ai_analysis = {
                        "intent": "get_available_data",
                        "tools_to_call": [
                            {
                                "tool_name": "get_pride_facets",
                                "parameters": {}
                            }
                        ]
                    }
                else:
                    # Search questions - get facets and projects
                    ai_analysis = {
                        "intent": "search_projects",
                        "tools_to_call": [
                            {
                                "tool_name": "get_pride_facets",
                                "parameters": {
                                    "keyword": user_message
                                }
                            },
                            {
                                "tool_name": "fetch_projects",
                                "parameters": {
                                    "keyword": user_message,
                                    "page_size": 25,
                                    "page": 0
                                }
                            }
                        ]
                    }
                await websocket.send_text(json.dumps({
                    "type": "progress",
                    "step": "AI Analysis",
                    "message": "Using fallback analysis due to error..."
                }))
        
        # Show AI analysis to user
        await websocket.send_text(json.dumps({
            "type": "ai_analysis",
            "intent": ai_analysis["intent"],
            "tools_to_call": ai_analysis["tools_to_call"]
        }))
        
        # Step 2: Execute the tools that AI determined are needed
        tool_results = []
        project_accessions = []
        facets_data = None
        
        for tool_call in ai_analysis["tools_to_call"]:
            tool_name = tool_call["tool_name"]
            parameters = tool_call["parameters"]
            logger.info(f"🔧 Executing tool: {tool_name} with parameters: {parameters}")
            
            # Execute tool with timeout protection
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(mcp_client.call_tool, tool_name, parameters),
                    timeout=60.0  # 60 second timeout for tool calls
                )
                tool_results.append({
                    "tool_name": tool_name,
                    "result": result
                })
                
                # If this was a get_pride_facets call, automatically call fetch_projects afterward
                if tool_name == "get_pride_facets" and result:
                    facets_data = result
                    logger.info(f"📊 Retrieved facets data")
                    
                    await websocket.send_text(json.dumps({
                        "type": "progress",
                        "step": "Analyzing Filters",
                        "message": "Analyzing available filters to refine search..."
                    }))
                    
                    # Extract the original keyword from the user's question
                    user_keyword = user_message.lower()
                    
                    # Analyze facets to find relevant filters with timeout
                    try:
                        filters = await asyncio.wait_for(
                            asyncio.to_thread(ai_service.analyze_facets_for_filters, facets_data, user_keyword),
                            timeout=30.0
                        )
                    except asyncio.TimeoutError:
                        logger.error("Facet analysis timed out")
                        filters = ""
                    
                    logger.info(f"🔍 Calling fetch_projects with keyword: {user_keyword}, filters: {filters}")
                    
                    await websocket.send_text(json.dumps({
                        "type": "progress",
                        "step": "Searching Projects",
                        "message": "Searching for projects in PRIDE Archive..."
                    }))
                    
                    # Always call fetch_projects after facets
                    try:
                        result = await asyncio.wait_for(
                            asyncio.to_thread(mcp_client.call_tool, "fetch_projects", {
                                "keyword": user_keyword,
                                "filters": filters,
                                "page_size": 25,
                                "page": 0
                            }),
                            timeout=60.0
                        )
                        
                        tool_results.append({
                            "tool_name": "fetch_projects",
                            "result": result
                        })
                        
                        logger.info(f"✅ fetch_projects completed")
                        
                    except asyncio.TimeoutError:
                        logger.error("fetch_projects timed out")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "error": "Project search timed out. Please try again."
                        }))
                    except Exception as e:
                        logger.error(f"❌ Error calling fetch_projects: {e}")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "error": f"Failed to call fetch_projects: {str(e)}"
                        }))

                # If this was a fetch_projects call, extract project accessions for details
                if tool_name == "fetch_projects":
                    logger.info(f"🔍 Processing fetch_projects result structure")
                    logger.info(f"🔍 Raw result: {json.dumps(result, indent=2)}")
                    
                    # Extract project accessions from the result - handle nested MCP structure
                    projects_data = None
                    if result.get("data"):
                        projects_data = result["data"]
                    elif result.get("result", {}).get("content"):
                        try:
                            content_text = result["result"]["content"][0].get("text", "")
                            if content_text:
                                parsed_content = json.loads(content_text)
                                projects_data = parsed_content.get("data")
                                logger.info(f"🔍 Extracted projects_data from nested structure")
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.error(f"❌ Error parsing fetch_projects content: {e}")
                    
                    # Handle different possible data structures
                    all_project_accessions = []
                    if projects_data:
                        if isinstance(projects_data, list):
                            # If it's a list of project objects or accessions
                            for project in projects_data:
                                if isinstance(project, str):
                                    # Direct accession string
                                    all_project_accessions.append(project)
                                elif isinstance(project, dict) and project.get("accession"):
                                    # Project object with accession field
                                    all_project_accessions.append(project["accession"])
                        elif isinstance(projects_data, dict) and projects_data.get("accessions"):
                            # Dictionary with accessions field
                            all_project_accessions = projects_data["accessions"]
                    
                    # If we still don't have accessions, try to extract from highlights
                    if not all_project_accessions and result.get("highlights", {}).get("project_accessions"):
                        all_project_accessions = result["highlights"]["project_accessions"]
                    
                    if all_project_accessions:
                        # Get top 3 project accessions for detailed retrieval
                        project_accessions = all_project_accessions[:3]
                        
                        logger.info(f"🔍 Found {len(all_project_accessions)} total projects, getting details for top 3: {project_accessions}")
                        
                        # Store all accessions in the result for AI to use
                        result["all_accessions"] = all_project_accessions
                        
                        # Also store in tool_results for AI to access
                        for tool_result in tool_results:
                            if tool_result["tool_name"] == "fetch_projects":
                                tool_result["result"]["all_accessions"] = all_project_accessions
                                break
                        
                        # Log additional info about the search results
                        if result.get("highlights"):
                            highlights = result["highlights"]
                            logger.info(f"📊 Search summary: {highlights.get('total_projects', 0)} total projects found for keyword '{highlights.get('keyword', 'unknown')}'")
                    else:
                        logger.info(f"🔍 No valid project data found in fetch_projects result")
                        project_accessions = []
                else:
                    logger.info(f"🔍 Tool {tool_name} result processed")
                
            except asyncio.TimeoutError:
                logger.error(f"Tool {tool_name} timed out")
                tool_results.append({
                    "tool_name": tool_name,
                    "result": {"error": f"Tool {tool_name} timed out"}
                })
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                tool_results.append({
                    "tool_name": tool_name,
                    "result": {"error": str(e)}
                })
        
        # Extract tools called for database storage
        tools_called = [result["tool_name"] for result in tool_results]
        
        # Step 2.5: Get project details for top projects
        if project_accessions and len(project_accessions) > 0 and len(tool_results) > 0:
            logger.info(f"📋 Getting details for {len(project_accessions)} project: {project_accessions}")
            
            await websocket.send_text(json.dumps({
                "type": "progress",
                "step": "Getting Project Details",
                "message": f"Retrieving detailed information for {len(project_accessions)} project..."
            }))
            
            successful_details = 0
            for i, accession in enumerate(project_accessions, 1):
                try:
                    logger.info(f"📋 Getting details for project {i}/{len(project_accessions)}: {accession}")
                    
                    # Send progress update to frontend
                    await websocket.send_text(json.dumps({
                        "type": "progress",
                        "message": f"Retrieving project details ({i}/{len(project_accessions)}): {accession}",
                        "progress": i,
                        "total": len(project_accessions)
                    }))
                    
                    # Get project details with proper error handling and timeout
                    try:
                        details_result = await asyncio.wait_for(
                            asyncio.to_thread(
                                mcp_client.call_tool, "get_project_details", {"project_accession": accession}
                            ),
                            timeout=45.0  # 45 second timeout per project
                        )
                    except asyncio.TimeoutError:
                        logger.error(f"❌ Timeout getting details for project {accession}")
                        # Skip this project and continue
                        continue
                    except Exception as e:
                        logger.error(f"❌ Error getting details for project {accession}: {e}")
                        # Skip this project and continue
                        continue
                    
                    # Extract title for logging - handle the nested MCP response structure
                    title = "No title"
                    if details_result.get("data", {}).get("title"):
                        title = details_result["data"]["title"]
                    elif details_result.get("result", {}).get("content"):
                        try:
                            content_text = details_result["result"]["content"][0].get("text", "")
                            if content_text:
                                parsed_content = json.loads(content_text)
                                title = parsed_content.get("title", "No title")
                        except (json.JSONDecodeError, KeyError):
                            title = "No title"
                    
                    logger.info(f"✅ Project details retrieved: {accession} - {title}")
                    
                    # Check if the result contains an error
                    if details_result.get("error"):
                        logger.warning(f"⚠️ Project details for {accession} contains error: {details_result.get('error')}")
                        # Still add to results but mark as error
                        tool_results.append({
                            "tool_name": "get_project_details",
                            "result": details_result,
                            "error": True
                        })
                    else:
                        # Add to tool results
                        tool_results.append({
                            "tool_name": "get_project_details",
                            "result": details_result
                        })
                    
                    successful_details += 1
                    
                except asyncio.TimeoutError:
                    logger.error(f"❌ Timeout getting details for project {accession}")
                    tool_results.append({
                        "tool_name": "get_project_details",
                        "result": {"error": f"Timeout getting details for {accession}"}
                    })
                    # Continue to next step even if this fails
                    break
                except Exception as e:
                    logger.error(f"❌ Error getting details for project {accession}: {e}")
                    tool_results.append({
                        "tool_name": "get_project_details",
                        "result": {"error": f"Failed to get details for {accession}: {str(e)}"}
                    })
                    # Continue to next step even if this fails
                    break
            
            logger.info(f"📋 Successfully retrieved details for {successful_details}/{len(project_accessions)} projects")
            
            # Send completion update to frontend
            await websocket.send_text(json.dumps({
                "type": "progress",
                "message": f"Completed retrieving details for {successful_details}/{len(project_accessions)} projects",
                "progress": len(project_accessions),
                "total": len(project_accessions),
                "completed": True
            }))
        
        # Step 3: Generate response using AI with timeout
        try:
            # Send progress update for AI response generation
            await websocket.send_text(json.dumps({
                "type": "progress",
                "message": "Generating AI response with project details...",
                "step": "AI Response Generation"
            }))
            
            logger.info(f"🤖 Starting AI response generation with {len(tool_results)} tool results")
            
            # Add context about available project accessions if we have them
            if project_accessions and len(project_accessions) > 0:
                # Add project accessions to the tool results for AI to use
                tool_results.append({
                    "tool_name": "project_accessions",
                    "result": {
                        "accessions": project_accessions,
                        "total_found": len(project_accessions),
                        "note": "Project details retrieval was temporarily disabled. Accessions are available for manual lookup.",
                        "ebi_links": [f"https://www.ebi.ac.uk/pride/archive/projects/{acc}" for acc in project_accessions]
                    }
                })
            
            logger.info(f"📊 Tool results summary: {len(tool_results)} tools called")
            for i, result in enumerate(tool_results):
                tool_name = result.get("tool_name", "unknown")
                logger.info(f"   {i+1}. {tool_name}")
            
            # Use AI to generate proper response
            logger.info("🚀 Calling AI service to generate response...")
            logger.info(f"   User message: {user_message[:100]}...")
            logger.info(f"   Intent: {ai_analysis.get('intent', 'unknown')}")
            logger.info(f"   Tool results count: {len(tool_results)}")
            logger.info(f"   AI service available: {ai_service is not None}")
            
            # Log the structure of tool_results for debugging
            for i, result in enumerate(tool_results):
                tool_name = result.get("tool_name", "unknown")
                result_data = result.get("result", {})
                logger.info(f"   Tool {i+1}: {tool_name} - Data keys: {list(result_data.keys()) if isinstance(result_data, dict) else 'not dict'}")
            
            # Call AI service with detailed logging
            start_ai_time = asyncio.get_event_loop().time()
            logger.info(f"   Starting AI service call at {start_ai_time}")
            
            response = await asyncio.wait_for(
                asyncio.to_thread(ai_service.generate_response, user_message, tool_results, ai_analysis["intent"]),
                timeout=60.0  # Back to 60 seconds for now
            )
            
            end_ai_time = asyncio.get_event_loop().time()
            ai_duration = end_ai_time - start_ai_time
            logger.info(f"✅ AI response generated successfully in {ai_duration:.2f}s (length: {len(response)})")
            logger.info(f"   Response preview: {response[:200]}...")
            
            # Send completion update for AI response generation
            await websocket.send_text(json.dumps({
                "type": "progress",
                "message": "AI response generated successfully!",
                "step": "AI Response Generation",
                "completed": True
            }))
        except asyncio.TimeoutError:
            logger.error("Response generation timed out, generating fallback response")
            
            # Send timeout update to frontend
            await websocket.send_text(json.dumps({
                "type": "progress",
                "message": "AI response generation timed out - generating fallback response",
                "step": "AI Response Generation",
                "error": True
            }))
            
            # Generate a fallback response based on the tool results
            try:
                response = generate_fallback_response(user_message, tool_results, ai_analysis["intent"])
                logger.info("✅ Fallback response generated successfully")
            except Exception as fallback_error:
                logger.error(f"Fallback response generation failed: {fallback_error}")
                response = "I apologize, but the response generation timed out. Please try again with a simpler query."
        except Exception as response_error:
            logger.error(f"Response generation failed: {response_error}")
            response = f"I apologize, but I encountered an error while generating a response: {str(response_error)}"
            
            # Send error update to frontend
            await websocket.send_text(json.dumps({
                "type": "progress",
                "message": f"AI response generation failed: {str(response_error)}",
                "step": "AI Response Generation",
                "error": True
            }))
        
        # Calculate response time
        end_time = asyncio.get_event_loop().time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        # Store question in database
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Use relative path for production compatibility
                api_url = "http://127.0.0.1:9000/api/questions"
                # In production, this will be: https://www.ebi.ac.uk/pride/services/mcp_api/questions
                # Send as JSON body since the API expects them in the request body
                json_data = {
                    "question": user_message,
                    "user_id": "web_ui_user",
                    "session_id": "web_session",
                    "response_time_ms": response_time_ms,
                    "tools_called": tools_called,
                    "response_length": len(response),
                    "success": success,
                    "error_message": error_message,
                    "metadata": {
                        "ai_service_available": ai_service is not None,
                        "intent": ai_analysis.get("intent", "unknown"),
                        "total_tools_called": len(tools_called)
                    }
                }
                logger.info(f"💾 Storing question in database: {user_message[:50]}...")
                response = await client.post(api_url, json=json_data)
                logger.info(f"✅ Question stored successfully: {response.status_code}")
        except Exception as db_error:
            logger.warning(f"Failed to store question in database: {db_error}")
        
        await websocket.send_text(json.dumps({
            "type": "assistant",
            "content": response
        }))
        
    except Exception as e:
        logger.error(f"Error handling user message: {e}")
        error_message = str(e)
        success = False
        
        # Calculate response time for error case
        end_time = asyncio.get_event_loop().time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        # Store error in database
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Use relative path for production compatibility
                api_url = "http://127.0.0.1:9000/api/questions"
                # In production, this will be: https://www.ebi.ac.uk/pride/services/mcp_api/questions
                # Send as JSON body since the API expects them in the request body
                json_data = {
                    "question": user_message,
                    "user_id": "web_ui_user",
                    "session_id": "web_session",
                    "response_time_ms": response_time_ms,
                    "tools_called": tools_called if 'tools_called' in locals() else [],
                    "response_length": 0,
                    "success": False,
                    "error_message": error_message,
                    "metadata": {
                        "ai_service_available": ai_service is not None,
                        "error_type": type(e).__name__
                    }
                }
                await client.post(api_url, json=json_data)
        except Exception as db_error:
            logger.warning(f"Failed to store error in database: {db_error}")
        
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))

def create_professional_ui(mcp_server_url: str, port: int = 9090):
    """Create and configure the professional UI server."""
    global mcp_client
    
    # Initialize MCP client
    mcp_client = MCPClient(mcp_server_url)
    
    # Test connection
    try:
        # Try to list tools to test connection
        tools = mcp_client.list_tools()
        logger.info(f"✅ MCP client connected successfully. Available tools: {len(tools)}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MCP server: {e}")
    
    return app

def generate_fallback_response(user_message: str, tool_results: list, intent: str) -> str:
    """Generate a fallback response when AI service is unavailable or times out."""
    try:
        # Extract project accessions if available
        project_accessions = []
        for result in tool_results:
            if result.get("tool_name") == "project_accessions":
                project_accessions = result.get("result", {}).get("accessions", [])
                break
        
        # Extract project details if available
        project_details = []
        for result in tool_results:
            if result.get("tool_name") == "get_project_details":
                details = result.get("result", {})
                if not details.get("error"):
                    project_details.append(details)
        
        # Generate response based on intent and available data
        if intent == "search_projects":
            if project_accessions:
                response = f"I found {len(project_accessions)} projects matching your query: {', '.join(project_accessions[:5])}"
                if len(project_accessions) > 5:
                    response += f" and {len(project_accessions) - 5} more."
                
                if project_details:
                    response += "\n\nHere are the details for the retrieved projects:\n"
                    for i, details in enumerate(project_details[:3], 1):
                        title = details.get("data", {}).get("title", "No title")
                        response += f"\n{i}. {title}"
                
                response += f"\n\nYou can view these projects at: https://www.ebi.ac.uk/pride/archive/projects/"
                return response
            else:
                return "I searched for projects but couldn't find any matching your criteria. Please try different keywords."
        
        elif intent == "get_available_data":
            return "I can help you explore the PRIDE Archive. You can search for projects by keywords, organisms, instruments, and more. What specific information are you looking for?"
        
        else:
            return "I've processed your request and retrieved some information. Please let me know if you need more specific details about any of the projects."
    
    except Exception as e:
        logger.error(f"Error generating fallback response: {e}")
        return "I apologize, but I encountered an error while processing your request. Please try again."


def run_professional_ui(mcp_server_url: str, port: int = 9090, host: str = "127.0.0.1"):
    """Run the professional UI server."""
    create_professional_ui(mcp_server_url, port)
    
    print(f"🚀 Starting Professional UI on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="PRIDE Archive Professional UI")
    parser.add_argument("--server-url", default="http://127.0.0.1:9001", help="MCP server URL")
    parser.add_argument("--port", type=int, default=9090, help="UI server port")
    parser.add_argument("--host", default="127.0.0.1", help="UI server host")
    
    args = parser.parse_args()
    run_professional_ui(args.server_url, args.port, args.host) 