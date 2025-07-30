# MCP Client Tools

A client library for interacting with Model Context Protocol (MCP) servers, with specific support for PRIDE Archive proteomics data.

## Features

- **MCP Client**: Async client for communicating with MCP servers
- **PRIDE Archive Integration**: Pre-configured tools for PRIDE EBI proteomics data
- **AI Integration**: Support for AI-powered data analysis
- **Web UI**: Built-in web interface for testing and exploration

## Installation

```bash
# Install from source
git clone https://github.com/yourusername/mcp-client-tools.git
cd mcp-client-tools
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
import asyncio
from mcp_client_tools import MCPClient

async def main():
    # Connect to MCP server
    client = MCPClient("http://127.0.0.1:9000")
    
    # List available tools
    tools = await client.list_tools()
    print(f"Available tools: {tools}")
    
    # Search for projects
    result = await client.call_tool("fetch_projects", {
        "keyword": "mouse",
        "filters": "organisms==Mus musculus (mouse)"
    })
    print(f"Found projects: {result}")
    
    await client.close()

asyncio.run(main())
```

### Web UI

Start the web interface:

```bash
python -m mcp_client_tools.web_ui --server-url http://127.0.0.1:9000
```

Then open http://127.0.0.1:9090 in your browser.

## Available Tools

### get_pride_facets
Get available filter values from PRIDE Archive.

```python
facets = await client.call_tool("get_pride_facets", {
    "facet_page_size": 100,
    "facet_page": 0
})
```

### fetch_projects
Search for proteomics projects in PRIDE Archive.

```python
projects = await client.call_tool("fetch_projects", {
    "keyword": "cancer",
    "filters": "organisms==Homo sapiens (human),diseases==Breast cancer",
    "page_size": 25,
    "page": 0
})
```

### get_project_details
Get detailed information about a specific project.

```python
details = await client.call_tool("get_project_details", {
    "project_accession": "PXD000001"
})
```

### get_project_files
Get file information for a project.

```python
files = await client.call_tool("get_project_files", {
    "project_accession": "PXD000001",
    "file_type": "mzML"
})
```

### analyze_with_ai
Analyze data using AI services.

```python
analysis = await client.call_tool("analyze_with_ai", {
    "data": "your_data_here",
    "analysis_type": "search_results",
    "context": "Additional context"
})
```

## Configuration

### AI Services

The client supports multiple AI providers:

- **Gemini**: Google's Gemini Pro
- **Claude**: Anthropic's Claude
- **OpenAI**: GPT models
- **Ollama**: Local LLM models

Configure AI services in `config/ai_config.json`:

```json
{
  "ai_provider": "gemini",
  "gemini": {
    "api_key": "your_gemini_api_key",
    "model": "gemini-2.0-flash-exp"
  }
}
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/mcp-client-tools.git
cd mcp-client-tools

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
isort src/

# Type checking
mypy src/
```

### Project Structure

```
mcp_client_tools/
├── src/
│   └── mcp_client_tools/
│       ├── __init__.py
│       ├── client.py        # MCPClient class
│       ├── tools.py         # PRIDE_EBI_TOOLS definition
│       ├── web_ui.py        # Web interface
│       ├── ai_service.py    # AI integration
│       └── config.py        # Configuration management
├── templates/               # HTML templates
├── static/                  # Static assets
├── tests/                   # Test files
├── pyproject.toml          # Build configuration
├── README.md               # This file
└── LICENSE                 # MIT License
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- PRIDE Archive team for providing the proteomics data
- MCP community for the protocol specification
- Contributors and maintainers

## Support

- Documentation: [GitHub Wiki](https://github.com/yourusername/mcp-client-tools/wiki)
- Issues: [GitHub Issues](https://github.com/yourusername/mcp-client-tools/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/mcp-client-tools/discussions) 