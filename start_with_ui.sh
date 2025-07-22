#!/bin/bash

# PRIDE MCP Server with Web UI Startup Script
# This script starts both the MCP server and a web UI for testing

set -e  # Exit on any error

echo "🧬 PRIDE MCP Server with Gemini Pro Integration & Web UI"
echo "========================================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. Please install uv first."
    echo "   Visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Check if Gemini API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set. AI features will be disabled."
    echo "   To enable AI features, set your API key:"
    echo "   export GEMINI_API_KEY='your_api_key_here'"
    echo ""
    read -p "Continue without AI features? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
else
    echo "✅ Gemini API key found. AI features enabled."
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
uv sync

# Test the server configuration
echo "🧪 Testing server configuration..."
if uv run python test_gemini.py > /dev/null 2>&1; then
    echo "✅ Server configuration test passed"
else
    echo "⚠️  Server configuration test failed, but continuing..."
fi

# Get server configuration
HOST=${HOST:-"127.0.0.1"}
MCP_PORT=${MCP_PORT:-"9000"}
UI_PORT=${UI_PORT:-"8080"}

echo ""
echo "🚀 Starting PRIDE MCP Server and Web UI..."
echo "   MCP Server: http://$HOST:$MCP_PORT"
echo "   Web UI: http://$HOST:$UI_PORT"
echo "   Health Check: http://$HOST:$UI_PORT/api/health"
echo ""
echo "📋 Available endpoints:"
echo "   - MCP Server: http://$HOST:$MCP_PORT"
echo "   - Web UI: http://$HOST:$UI_PORT"
echo "   - Health Check: http://$HOST:$UI_PORT/api/health"
echo "   - OpenAPI Docs: http://$HOST:$MCP_PORT/docs"
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $MCP_PID $UI_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start MCP server in background
echo "🔧 Starting MCP server on port $MCP_PORT..."
uv run python main.py --host "$HOST" --port "$MCP_PORT" &
MCP_PID=$!

# Wait a moment for MCP server to start
sleep 3

# Check if MCP server is running
if ! kill -0 $MCP_PID 2>/dev/null; then
    echo "❌ Failed to start MCP server"
    exit 1
fi

echo "✅ MCP server started (PID: $MCP_PID)"

# Start Web UI in background
echo "🌐 Starting Web UI on port $UI_PORT..."
uv run python ui_test_server.py &
UI_PID=$!

# Wait a moment for Web UI to start
sleep 3

# Check if Web UI is running
if ! kill -0 $UI_PID 2>/dev/null; then
    echo "❌ Failed to start Web UI"
    kill $MCP_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Web UI started (PID: $UI_PID)"
echo ""
echo "🎉 All services are running!"
echo "   Open your browser and go to: http://$HOST:$UI_PORT"
echo ""
echo "📝 Quick Start Guide:"
echo "   1. Open http://$HOST:$UI_PORT in your browser"
echo "   2. Try searching for 'cancer' projects"
echo "   3. Get details for a specific project (e.g., PXD000001)"
echo "   4. Use Gemini Pro analysis for AI-powered insights"
echo ""

# Wait for user to stop
echo "⏳ Services are running. Press Ctrl+C to stop..."
wait 