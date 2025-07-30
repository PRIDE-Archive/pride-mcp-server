
# PRIDE Archive MCP Server - Integration Guide

## Server Information
- **Name:** PRIDE Archive MCP Server
- **URL:** http://localhost:9000
- **Description:** Access proteomics data from the PRIDE Archive database

## Available Tools


### get_pride_facets
**Description:** Get available filters and facets from PRIDE Archive

**Parameters:**
- `facet_page_size`: Number of facet values per page (default: 100)
- `facet_page`: Page number for pagination (default: 0)
- `keyword`: Optional keyword for filtering facets

### fetch_projects
**Description:** Search for proteomics projects in PRIDE Archive

**Parameters:**
- `keyword`: Search keyword (e.g., 'cancer', 'mouse', 'proteomics')
- `page_size`: Number of results per page (default: 25)
- `page`: Page number for pagination (default: 0)
- `filters`: Comma-separated filters from facets

### get_project_details
**Description:** Get detailed information about a specific project

**Parameters:**
- `project_accession`: PRIDE project accession (e.g., 'PXD000001')

### get_project_files
**Description:** Get file information for a specific project

**Parameters:**
- `project_accession`: PRIDE project accession (e.g., 'PXD000001')
- `file_type`: Optional filter for specific file types

## Integration Instructions


### Claude Desktop
Add PRIDE Archive MCP Server to Claude Desktop

**Instructions:**
1. Open Claude Desktop
2. Go to Settings → Extensions
3. Click 'Add Extension'
4. Select 'MCP (Model Context Protocol)'
5. Enter the following configuration:

**Server URL:** http://localhost:9000
**Server Name:** PRIDE Archive MCP Server
**Description:** Access proteomics data from PRIDE Archive

6. Click 'Add' to save the configuration
7. Restart Claude Desktop if prompted

**Configuration JSON:**
```json
{
  "mcpServers": {
    "pride-archive": {
      "command": "python",
      "args": [
        "-m",
        "mcp.server.stdio"
      ],
      "env": {
        "MCP_SERVER_URL": "http://localhost:9000"
      }
    }
  }
}
```

---

### ChatGPT (with MCP Plugin)
Add PRIDE Archive MCP Server to ChatGPT

**Instructions:**
1. Install the MCP plugin for ChatGPT
2. Open ChatGPT and go to Settings
3. Navigate to Plugins section
4. Add new MCP server with:

**Server URL:** http://localhost:9000
**Server Name:** PRIDE Archive MCP Server

5. Save and restart ChatGPT

**Configuration JSON:**
```json
{
  "mcp_servers": [
    {
      "name": "pride-archive",
      "url": "http://localhost:9000",
      "description": "Access proteomics data from PRIDE Archive"
    }
  ]
}
```

---

### Cursor IDE
Add PRIDE Archive MCP Server to Cursor

**Instructions:**
1. Open Cursor IDE
2. Go to Settings (Cmd/Ctrl + ,)
3. Search for 'MCP' or 'Model Context Protocol'
4. Add new MCP server configuration:

**Server URL:** http://localhost:9000
**Server Name:** PRIDE Archive MCP Server

5. Save the configuration
6. Restart Cursor if needed

**Configuration JSON:**
```json
{
  "mcp.servers": {
    "pride-archive": {
      "url": "http://localhost:9000",
      "name": "PRIDE Archive MCP Server",
      "description": "Access proteomics data from PRIDE Archive"
    }
  }
}
```

---

### VS Code (with MCP Extension)
Add PRIDE Archive MCP Server to VS Code

**Instructions:**
1. Install the MCP extension for VS Code
2. Open VS Code settings (Cmd/Ctrl + ,)
3. Search for 'MCP'
4. Add server configuration:

**Server URL:** http://localhost:9000
**Server Name:** PRIDE Archive MCP Server

5. Save and reload VS Code

**Configuration JSON:**
```json
{
  "mcp.servers": [
    {
      "name": "pride-archive",
      "url": "http://localhost:9000",
      "description": "Access proteomics data from PRIDE Archive"
    }
  ]
}
```

---

### Custom MCP Client
Generic configuration for custom MCP clients

**Instructions:**
1. Ensure the PRIDE MCP Server is running on http://localhost:9000
2. Configure your MCP client with:

**Server URL:** http://localhost:9000
**Server Name:** PRIDE Archive MCP Server
**Description:** Access proteomics data from PRIDE Archive

3. Available tools:
   - get_pride_facets: Get available filters and facets
   - fetch_projects: Search for proteomics projects
   - get_project_details: Get detailed project information
   - get_project_files: Get project file information

**Configuration JSON:**
```json
{
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
```

---
