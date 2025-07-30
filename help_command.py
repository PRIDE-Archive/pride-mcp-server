#!/usr/bin/env python3
"""
Help Command for PRIDE MCP Server
Provides quick access to integration instructions
"""

import json
import sys
from pathlib import Path

def show_quick_help():
    """Show quick help information."""
    print("🔧 PRIDE Archive MCP Server - Quick Help")
    print("=" * 50)
    print()
    print("📋 Server Information:")
    print("  URL: http://localhost:9000")
    print("  Name: PRIDE Archive MCP Server")
    print("  Description: Access proteomics data from PRIDE Archive")
    print()
    print("🛠️  Available Tools:")
    print("  - get_pride_facets: Get available filters and facets")
    print("  - fetch_projects: Search for proteomics projects")
    print("  - get_project_details: Get detailed project information")
    print("  - get_project_files: Get project file information")
    print()
    print("📖 Integration Guides:")
    print("  - Claude Desktop: help/claude_desktop_config.json")
    print("  - ChatGPT: help/chatgpt_config.json")
    print("  - Cursor IDE: help/cursor_config.json")
    print("  - VS Code: help/vscode_config.json")
    print("  - Custom: help/custom_config.json")
    print()
    print("📄 Full Documentation: help/README.md")
    print()
    print("💡 Quick Start:")
    print("  1. Ensure server is running: uv run python start_services.py")
    print("  2. Add MCP server to your AI tool using the config files above")
    print("  3. Start asking questions about proteomics data!")

def show_tool_help(tool_name: str = None):
    """Show detailed help for a specific tool."""
    tools = {
        "get_pride_facets": {
            "description": "Get available filters and facets from PRIDE Archive",
            "parameters": {
                "facet_page_size": "Number of facet values per page (default: 100)",
                "facet_page": "Page number for pagination (default: 0)",
                "keyword": "Optional keyword for filtering facets"
            },
            "example": {
                "keyword": "cancer",
                "facet_page_size": 100,
                "facet_page": 0
            }
        },
        "fetch_projects": {
            "description": "Search for proteomics projects in PRIDE Archive",
            "parameters": {
                "keyword": "Search keyword (e.g., 'cancer', 'mouse', 'proteomics')",
                "page_size": "Number of results per page (default: 25)",
                "page": "Page number for pagination (default: 0)",
                "filters": "Comma-separated filters from facets"
            },
            "example": {
                "keyword": "mouse cancer",
                "page_size": 25,
                "page": 0,
                "filters": "organism:Mus musculus,disease:cancer"
            }
        },
        "get_project_details": {
            "description": "Get detailed information about a specific project",
            "parameters": {
                "project_accession": "PRIDE project accession (e.g., 'PXD000001')"
            },
            "example": {
                "project_accession": "PXD000001"
            }
        },
        "get_project_files": {
            "description": "Get file information for a specific project",
            "parameters": {
                "project_accession": "PRIDE project accession (e.g., 'PXD000001')",
                "file_type": "Optional filter for specific file types"
            },
            "example": {
                "project_accession": "PXD000001",
                "file_type": "mzML"
            }
        }
    }
    
    if tool_name and tool_name in tools:
        tool = tools[tool_name]
        print(f"🔧 Tool: {tool_name}")
        print("=" * 40)
        print(f"Description: {tool['description']}")
        print()
        print("Parameters:")
        for param, desc in tool['parameters'].items():
            print(f"  - {param}: {desc}")
        print()
        print("Example:")
        print(f"  {json.dumps(tool['example'], indent=2)}")
    else:
        print("Available tools:")
        for tool_name in tools.keys():
            print(f"  - {tool_name}")
        print()
        print("Usage: python3 help_command.py tool <tool_name>")

def show_integration_help(tool_name: str = None):
    """Show integration help for a specific tool."""
    integrations = {
        "claude": {
            "name": "Claude Desktop",
            "steps": [
                "1. Open Claude Desktop",
                "2. Go to Settings → Extensions",
                "3. Click 'Add Extension'",
                "4. Select 'MCP (Model Context Protocol)'",
                "5. Enter Server URL: http://localhost:9000",
                "6. Enter Server Name: PRIDE Archive MCP Server",
                "7. Click 'Add' and restart if prompted"
            ]
        },
        "cursor": {
            "name": "Cursor IDE",
            "steps": [
                "1. Open Cursor IDE",
                "2. Go to Settings (Cmd/Ctrl + ,)",
                "3. Search for 'MCP' or 'Model Context Protocol'",
                "4. Add new MCP server configuration:",
                "   - Server URL: http://localhost:9000",
                "   - Server Name: PRIDE Archive MCP Server",
                "5. Save and restart Cursor if needed"
            ]
        },
        "chatgpt": {
            "name": "ChatGPT (with MCP Plugin)",
            "steps": [
                "1. Install the MCP plugin for ChatGPT",
                "2. Open ChatGPT and go to Settings",
                "3. Navigate to Plugins section",
                "4. Add new MCP server:",
                "   - Server URL: http://localhost:9000",
                "   - Server Name: PRIDE Archive MCP Server",
                "5. Save and restart ChatGPT"
            ]
        }
    }
    
    if tool_name and tool_name in integrations:
        integration = integrations[tool_name]
        print(f"🔧 {integration['name']} Integration")
        print("=" * 40)
        for step in integration['steps']:
            print(step)
    else:
        print("Available integrations:")
        for key in integrations.keys():
            print(f"  - {key}")
        print()
        print("Usage: python3 help_command.py integration <tool_name>")

def main():
    """Main help command."""
    if len(sys.argv) < 2:
        show_quick_help()
        return
    
    command = sys.argv[1]
    
    if command == "tool":
        tool_name = sys.argv[2] if len(sys.argv) > 2 else None
        show_tool_help(tool_name)
    elif command == "integration":
        tool_name = sys.argv[2] if len(sys.argv) > 2 else None
        show_integration_help(tool_name)
    elif command == "generate":
        # Regenerate help files
        try:
            from help_config import MCPHelpConfig
            help_config = MCPHelpConfig()
            help_config.save_help_files()
            print("✅ Help files regenerated successfully!")
        except ImportError:
            print("❌ Could not import help_config. Make sure help_config.py exists.")
    else:
        print("Usage:")
        print("  python3 help_command.py                    # Show quick help")
        print("  python3 help_command.py tool [tool_name]   # Show tool help")
        print("  python3 help_command.py integration [tool] # Show integration help")
        print("  python3 help_command.py generate           # Regenerate help files")

if __name__ == "__main__":
    main() 