#!/bin/bash
# PRIDE MCP Server - Start Services Script
# Always uses uv run to ensure dependencies are properly loaded

echo "🚀 Starting PRIDE MCP Server services..."
echo "📋 Using uv run to ensure all dependencies are loaded"
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed or not in PATH"
    echo "💡 Install uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Start the services
echo "🔧 Running: uv run python start_services.py"
echo ""

uv run python start_services.py 