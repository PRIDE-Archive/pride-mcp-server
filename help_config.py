#!/usr/bin/env python3
"""
Help Configuration System for PRIDE MCP Server
Provides instructions for adding the MCP server to various AI tools
"""

import json
import os
from typing import Dict, List

class MCPHelpConfig:
    """Help configuration for MCP server integration."""
    
    def __init__(self):
        self.server_url = "http://localhost:9000"
        self.server_name = "PRIDE Archive MCP Server"
        self.server_description = "Access proteomics data from the PRIDE Archive database"
        
    def get_tool_configs(self) -> Dict[str, Dict]:
        """Get configuration instructions for different AI tools."""
        return {
            "claude_desktop": {
                "name": "Claude Desktop",
                "description": "Add PRIDE Archive MCP Server to Claude Desktop",
                "instructions": [
                    "1. Open Claude Desktop",
                    "2. Go to Settings → Extensions",
                    "3. Click 'Add Extension'",
                    "4. Select 'MCP (Model Context Protocol)'",
                    "5. Enter the following configuration:",
                    "",
                    "**Server URL:** http://localhost:9000",
                    "**Server Name:** PRIDE Archive MCP Server",
                    "**Description:** Access proteomics data from PRIDE Archive",
                    "",
                    "6. Click 'Add' to save the configuration",
                    "7. Restart Claude Desktop if prompted"
                ],
                "config_json": {
                    "mcpServers": {
                        "pride-archive": {
                            "command": "python",
                            "args": ["-m", "mcp.server.stdio"],
                            "env": {
                                "MCP_SERVER_URL": "http://localhost:9000"
                            }
                        }
                    }
                }
            },
            
            "chatgpt": {
                "name": "ChatGPT (with MCP Plugin)",
                "description": "Add PRIDE Archive MCP Server to ChatGPT",
                "instructions": [
                    "1. Install the MCP plugin for ChatGPT",
                    "2. Open ChatGPT and go to Settings",
                    "3. Navigate to Plugins section",
                    "4. Add new MCP server with:",
                    "",
                    "**Server URL:** http://localhost:9000",
                    "**Server Name:** PRIDE Archive MCP Server",
                    "",
                    "5. Save and restart ChatGPT"
                ],
                "config_json": {
                    "mcp_servers": [
                        {
                            "name": "pride-archive",
                            "url": "http://localhost:9000",
                            "description": "Access proteomics data from PRIDE Archive"
                        }
                    ]
                }
            },
            
            "cursor": {
                "name": "Cursor IDE",
                "description": "Add PRIDE Archive MCP Server to Cursor",
                "instructions": [
                    "1. Open Cursor IDE",
                    "2. Go to Settings (Cmd/Ctrl + ,)",
                    "3. Search for 'MCP' or 'Model Context Protocol'",
                    "4. Add new MCP server configuration:",
                    "",
                    "**Server URL:** http://localhost:9000",
                    "**Server Name:** PRIDE Archive MCP Server",
                    "",
                    "5. Save the configuration",
                    "6. Restart Cursor if needed"
                ],
                "config_json": {
                    "mcp.servers": {
                        "pride-archive": {
                            "url": "http://localhost:9000",
                            "name": "PRIDE Archive MCP Server",
                            "description": "Access proteomics data from PRIDE Archive"
                        }
                    }
                }
            },
            
            "vscode": {
                "name": "VS Code (with MCP Extension)",
                "description": "Add PRIDE Archive MCP Server to VS Code",
                "instructions": [
                    "1. Install the MCP extension for VS Code",
                    "2. Open VS Code settings (Cmd/Ctrl + ,)",
                    "3. Search for 'MCP'",
                    "4. Add server configuration:",
                    "",
                    "**Server URL:** http://localhost:9000",
                    "**Server Name:** PRIDE Archive MCP Server",
                    "",
                    "5. Save and reload VS Code"
                ],
                "config_json": {
                    "mcp.servers": [
                        {
                            "name": "pride-archive",
                            "url": "http://localhost:9000",
                            "description": "Access proteomics data from PRIDE Archive"
                        }
                    ]
                }
            },
            
            "custom": {
                "name": "Custom MCP Client",
                "description": "Generic configuration for custom MCP clients",
                "instructions": [
                    "1. Ensure the PRIDE MCP Server is running on http://localhost:9000",
                    "2. Configure your MCP client with:",
                    "",
                    "**Server URL:** http://localhost:9000",
                    "**Server Name:** PRIDE Archive MCP Server",
                    "**Description:** Access proteomics data from PRIDE Archive",
                    "",
                    "3. Available tools:",
                    "   - get_pride_facets: Get available filters and facets",
                    "   - fetch_projects: Search for proteomics projects",
                    "   - get_project_details: Get detailed project information",
                    "   - get_project_files: Get project file information"
                ],
                "config_json": {
                    "server_url": "http://localhost:9000",
                    "server_name": "PRIDE Archive MCP Server",
                    "description": "Access proteomics data from PRIDE Archive",
                    "tools": [
                        "get_pride_facets",
                        "fetch_projects", 
                        "get_project_details",
                        "get_project_files"
                    ]
                }
            }
        }
    
    def get_server_info(self) -> Dict:
        """Get server information for display."""
        return {
            "name": self.server_name,
            "url": self.server_url,
            "description": self.server_description,
            "tools": [
                {
                    "name": "get_pride_facets",
                    "description": "Get available filters and facets from PRIDE Archive",
                    "parameters": {
                        "facet_page_size": "Number of facet values per page (default: 100)",
                        "facet_page": "Page number for pagination (default: 0)",
                        "keyword": "Optional keyword for filtering facets"
                    }
                },
                {
                    "name": "fetch_projects",
                    "description": "Search for proteomics projects in PRIDE Archive",
                    "parameters": {
                        "keyword": "Search keyword (e.g., 'cancer', 'mouse', 'proteomics')",
                        "page_size": "Number of results per page (default: 25)",
                        "page": "Page number for pagination (default: 0)",
                        "filters": "Comma-separated filters from facets"
                    }
                },
                {
                    "name": "get_project_details",
                    "description": "Get detailed information about a specific project",
                    "parameters": {
                        "project_accession": "PRIDE project accession (e.g., 'PXD000001')"
                    }
                },
                {
                    "name": "get_project_files",
                    "description": "Get file information for a specific project",
                    "parameters": {
                        "project_accession": "PRIDE project accession (e.g., 'PXD000001')",
                        "file_type": "Optional filter for specific file types"
                    }
                }
            ]
        }
    
    def generate_help_page(self) -> str:
        """Generate a complete help page with all configurations."""
        configs = self.get_tool_configs()
        server_info = self.get_server_info()
        
        help_content = f"""
# PRIDE Archive MCP Server - Integration Guide

## Server Information
- **Name:** {server_info['name']}
- **URL:** {server_info['url']}
- **Description:** {server_info['description']}

## Available Tools

"""
        
        for tool in server_info['tools']:
            help_content += f"""
### {tool['name']}
**Description:** {tool['description']}

**Parameters:**
"""
            for param, desc in tool['parameters'].items():
                help_content += f"- `{param}`: {desc}\n"
        
        help_content += "\n## Integration Instructions\n\n"
        
        for tool_key, config in configs.items():
            help_content += f"""
### {config['name']}
{config['description']}

**Instructions:**
"""
            for instruction in config['instructions']:
                help_content += f"{instruction}\n"
            
            help_content += f"""
**Configuration JSON:**
```json
{json.dumps(config['config_json'], indent=2)}
```

---
"""
        
        return help_content
    
    def save_help_files(self, output_dir: str = "help"):
        """Save help files to disk."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save main help page
        help_content = self.generate_help_page()
        with open(f"{output_dir}/README.md", "w") as f:
            f.write(help_content)
        
        # Save individual tool configs
        configs = self.get_tool_configs()
        for tool_key, config in configs.items():
            config_file = f"{output_dir}/{tool_key}_config.json"
            with open(config_file, "w") as f:
                json.dump(config['config_json'], f, indent=2)
        
        # Save server info
        server_info = self.get_server_info()
        with open(f"{output_dir}/server_info.json", "w") as f:
            json.dump(server_info, f, indent=2)
        
        print(f"✅ Help files saved to {output_dir}/")
        print(f"📄 Main help: {output_dir}/README.md")
        print(f"⚙️  Tool configs: {output_dir}/*_config.json")
        print(f"ℹ️  Server info: {output_dir}/server_info.json")

def main():
    """Main function to generate help files."""
    help_config = MCPHelpConfig()
    
    print("🔧 PRIDE Archive MCP Server - Help Configuration Generator")
    print("=" * 60)
    
    # Generate and save help files
    help_config.save_help_files()
    
    # Display quick reference
    print("\n📋 Quick Reference:")
    print(f"Server URL: {help_config.server_url}")
    print(f"Server Name: {help_config.server_name}")
    print(f"Description: {help_config.server_description}")
    
    print("\n🛠️  Available Tools:")
    server_info = help_config.get_server_info()
    for tool in server_info['tools']:
        print(f"  - {tool['name']}: {tool['description']}")

if __name__ == "__main__":
    main() 