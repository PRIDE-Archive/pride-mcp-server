# PRIDE MCP Server Setup Guide

A comprehensive guide to set up and use the PRIDE Archive MCP server with Cursor for proteomics data exploration.

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd pride-mcp-server
```

### 2. Install Dependencies
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 3. Set Environment Variables
```bash
# Set your Gemini API key
export GEMINI_API_KEY="your_gemini_api_key_here"
export GEMINI_MODEL="gemini-2.0-flash-exp"
```

### 4. Start the Servers

#### Option A: MCP Server Only (for Cursor)
```bash
# Start the MCP server on port 9000
uv run python main.py --host 127.0.0.1 --port 9000
```

#### Option B: MCP Server + Web UI (for both Cursor and browser)
```bash
# Start both MCP server (port 9000) and web UI (port 8080)
./start_with_ui.sh
```

#### Option C: Manual Start (if script doesn't work)
```bash
# Terminal 1: Start MCP server
export GEMINI_API_KEY="your_gemini_api_key_here"
export GEMINI_MODEL="gemini-2.0-flash-exp"
uv run python main.py --host 127.0.0.1 --port 9000

# Terminal 2: Start web UI
uv run python ui_test_server.py --host 127.0.0.1 --port 8080
```

The servers should start with output like:
```
🚀 Starting PRIDE MCP Server with Gemini Pro integration...
✅ Gemini Pro integration enabled
INFO:     Uvicorn running on http://127.0.0.1:9000

# And for web UI:
INFO:     Uvicorn running on http://127.0.0.1:8080
```

## 🔧 Configure Cursor MCP

### 1. URL-based Configuration
If you prefer URL-based configuration:

```json
{
  "mcpServers": {
    "pride-mcp-server": {
      "url": "http://127.0.0.1:9000/mcp"
    }
  }
}
```

### 2. Restart Cursor
After editing the MCP configuration, restart Cursor to load the new settings.

## ✅ Verify Setup

### Check MCP Server Status
The MCP indicator in Cursor should turn **green** when properly connected.

### Test Connection
In Cursor chat, try asking:
```
What tools are available in the PRIDE MCP server?
```

You should see the available tools listed.

### Access Web UI (if started)
If you started the web UI, open your browser and go to:
```
http://127.0.0.1:8080
```

You can test queries directly in the web interface and compare results with Cursor.

## 🧬 Available Tools

The PRIDE MCP server provides these tools:

### 1. `get_pride_facets`
- **Purpose**: Get available filter values from PRIDE Archive
- **Use**: Always call this first before searching
- **Parameters**: `facet_page_size`, `facet_page`

### 2. `fetch_projects`
- **Purpose**: Search for proteomics projects
- **Use**: Main search function with filters
- **Parameters**: `keyword`, `filters`, `page_size`, `page`, `sort_direction`, `sort_fields`

### 3. `get_project_details`
- **Purpose**: Get detailed information about a specific project
- **Use**: After finding project accessions
- **Parameters**: `project_accession`

### 4. `get_project_files`
- **Purpose**: Get file information for a project
- **Use**: To see available data files
- **Parameters**: `project_accession`, `file_type`

## 🔍 Example Queries

### Basic Search
```
Search for human breast cancer proteomics studies
```

### Advanced Search with Filters
```
Find mouse proteomics studies using SWATH MS on cancer samples
```

### Date-Range Search
```
Search for Alzheimer's disease datasets with TMT quantification published between 2023 and 2025
```

### Specific Technology Search
```
Find yeast proteomics studies using MaxQuant
```

### Compare Cursor vs Web UI
Try the same query in both Cursor chat and the web UI to compare:
- **Cursor**: Direct MCP tool calls with detailed responses
- **Web UI**: Gemini Pro orchestration with natural language responses

## 📊 Filter Examples

### Organisms
- `organisms==Homo sapiens (human)`
- `organisms==Mus musculus (mouse)`
- `organisms==Saccharomyces cerevisiae (baker's yeast)`

### Experiment Types
- `experimentTypes==SWATH MS`
- `experimentTypes==Shotgun proteomics`
- `experimentTypes==Data-independent acquisition`

### Diseases
- `diseases==Alzheimer's disease`
- `diseases==Breast cancer`
- `diseases==Lung cancer`

### Quantification Methods
- `quantificationMethods==TMT`
- `quantificationMethods==SILAC`
- `quantificationMethods==iTRAQ`

### Software
- `softwares==MaxQuant`
- `softwares==Mascot`
- `softwares==Proteome Discoverer`

### Date Filtering
For date ranges, call `fetch_projects` multiple times:
- `submissionDate==2023`
- `submissionDate==2024`
- `submissionDate==2025`

## 🎯 Best Practices

### 1. Always Start with Facets
```bash
# First, get available filter values
get_pride_facets
```

### 2. Use Specific Keywords
- ✅ Good: `cancer`, `alzheimer`, `proteomics`
- ❌ Avoid: `studies`, `data`, `research`

### 3. Combine Filters Effectively
```bash
# Example: Mouse + SWATH MS + Cancer
filters="organisms==Mus musculus (mouse),experimentTypes==SWATH MS"
keyword="cancer"
```

### 4. Date Range Queries
For "2023-2025", make separate calls:
1. `submissionDate==2023`
2. `submissionDate==2024`
3. `submissionDate==2025`

## 🚨 Troubleshooting

### MCP Indicator is Red/Yellow
1. **Check server is running**: `curl http://127.0.0.1:9000/health`
2. **Verify MCP config**: Check `~/.cursor/mcp.json` syntax
3. **Restart Cursor**: After config changes
4. **Check logs**: Look for error messages in terminal

### Web UI Not Loading
1. **Check if UI server is running**: `curl http://127.0.0.1:8080`
2. **Verify port 8080 is free**: `lsof -i :8080`
3. **Check UI server logs**: Look for error messages in the UI terminal
4. **Try manual start**: Use Option C above to start UI separately

### No Results Found
1. **Check facets first**: Use `get_pride_facets` to see available values
2. **Verify filter syntax**: Use exact values from facets
3. **Try broader search**: Remove some filters to get more results
4. **Check keyword**: Use specific, relevant keywords

### Server Won't Start
1. **Check dependencies**: `uv sync`
2. **Verify API key**: `echo $GEMINI_API_KEY`
3. **Check port availability**: Ensure port 9000 is free
4. **Check Python version**: Ensure Python 3.8+ is installed

## 📝 Example Workflow

### Complete Search Example
```
User: "Find human breast cancer proteomics studies from 2023"

Assistant: Let me help you find human breast cancer proteomics studies from 2023.

First, let me get the available filter values:
[Call get_pride_facets]

Now, let me search for the studies:
[Call fetch_projects with filters="organisms==Homo sapiens (human),organismsPart==Breast,submissionDate==2023" and keyword="cancer"]

I found X projects. Let me get details for the top result:
[Call get_project_details with project_accession]

Here are the results...
```

## 🔗 Useful Links

- **PRIDE Archive**: https://www.ebi.ac.uk/pride/
- **MCP Documentation**: https://modelcontextprotocol.io/
- **Cursor Documentation**: https://cursor.sh/docs

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Gemini API key is valid
3. Ensure all dependencies are installed
4. Check the server logs for error messages

---

**Happy Proteomics Data Exploration! 🧬🔬** 