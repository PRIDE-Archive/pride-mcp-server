# PRIDE MCP Server

A Model Context Protocol (MCP) server for accessing PRIDE Archive proteomics data.

## Overview

This MCP server provides tools for searching and retrieving proteomics data from the PRIDE Archive database. It implements the Model Context Protocol to enable AI assistants to access proteomics data programmatically. The system uses an intelligent search approach that always calls facets first to determine optimal filters, then performs enhanced searches with those filters for more precise results. It automatically retrieves detailed project information and presents results in a clean, professional format with direct links to EBI project pages.

## Features

- **PRIDE Archive Integration**: Direct access to PRIDE EBI proteomics database
- **Intelligent Search**: AI-powered natural language search with automatic project details retrieval
- **Facets-Enhanced Search**: Always calls facets first to determine optimal filters for more precise searches
- **Clean Response Format**: Professional, research-oriented responses with direct links to EBI project pages
- **Advanced Filtering**: Automatic filter selection based on user keywords and available facets
- **Project Details**: Retrieve detailed information about proteomics projects
- **File Access**: Get file information and download links
- **MCP Protocol**: Standard Model Context Protocol implementation
- **Analytics & Database**: SQLite database for tracking questions, response times, and usage analytics
- **Slack Integration**: Real-time notifications and analytics reports via Slack webhooks
- **API Endpoints**: RESTful API for accessing analytics data and system statistics
- **Analytics Dashboard**: Web-based dashboard for visualizing usage patterns and system performance

## Quick Start

### Prerequisites

- Python 3.8+
- uv (recommended) or pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd pride-mcp-server

# Install dependencies
uv sync

# Start both MCP server and AI conversational UI
uv run python start_services.py

# Alternative: Use the convenience script
./start.sh
```

The services will start on:
- MCP Server: http://127.0.0.1:9000
- AI Conversational UI: http://127.0.0.1:9090
- Analytics Dashboard: http://127.0.0.1:8080/analytics_dashboard.html

## MCP Server Integration

The PRIDE Archive MCP Server can be integrated with various AI tools like Claude Desktop, ChatGPT, Cursor IDE, and more.

### Quick Help
```bash
uv run python help_command.py
```

### Integration Guides
- **Claude Desktop:** `uv run python help_command.py integration claude`
- **Cursor IDE:** `uv run python help_command.py integration cursor`
- **ChatGPT:** `uv run python help_command.py integration chatgpt`

### Tool Documentation
```bash
uv run python help_command.py tool <tool_name>
```

### Configuration Files
All integration configurations are available in the `help/` directory:
- `help/README.md` - Complete integration guide
- `help/claude_desktop_config.json` - Claude Desktop configuration
- `help/cursor_config.json` - Cursor IDE configuration
- `help/chatgpt_config.json` - ChatGPT configuration
- `help/vscode_config.json` - VS Code configuration
- `help/custom_config.json` - Generic configuration

## Available Tools

### get_pride_facets
Retrieves available filter values from PRIDE Archive.

**Parameters:**
- `facet_page_size` (optional): Number of facet values per page (default: 100)
- `facet_page` (optional): Page number for pagination (default: 0)

### fetch_projects
Searches for proteomics projects in PRIDE Archive.

**Parameters:**
- `keyword` (required): Search keyword
- `filters` (optional): Comma-separated filters using exact values from facets
- `page_size` (optional): Results per page (default: 25)
- `page` (optional): Page number (default: 0)
- `sort_direction` (optional): ASC or DESC (default: DESC)
- `sort_fields` (optional): Fields to sort by (default: downloadCount)

### get_project_details
Gets detailed information about a specific PRIDE project.

**Parameters:**
- `project_accession` (required): PRIDE project accession (e.g., PXD000001)

### get_project_files
Gets file information for a specific PRIDE project.

**Parameters:**
- `project_accession` (required): PRIDE project accession
- `file_type` (optional): Filter for specific file types

### analyze_with_ai
Analyzes proteomics data using AI services.

**Parameters:**
- `data` (required): Data to analyze (JSON string or text)
- `analysis_type` (optional): Type of analysis (default: general)
- `context` (optional): Additional context

## Usage Examples

### Using with MCP Client

```python
from mcp_client_tools import MCPClient

# Connect to the server
client = MCPClient("http://127.0.0.1:9000")

# Get available facets
facets = client.call_tool("get_pride_facets", {})

# Search for projects
projects = client.call_tool("fetch_projects", {
    "keyword": "cancer",
    "filters": "organisms==Homo sapiens (human),diseases==Breast cancer"
})
```

### Using with AI Assistants

The server can be integrated with AI assistants that support the MCP protocol:

```bash
# Example with Claude Desktop
claude --mcp-server pride-mcp-server
```

## Analytics & Database Features

### Database Storage

The system automatically stores all questions and responses in a SQLite database (`pride_questions.db`) with the following information:

- **Questions**: User queries with timestamps
- **Response Times**: Performance metrics for each interaction
- **Tool Usage**: Which MCP tools were called
- **Success/Failure**: Whether the request completed successfully
- **Metadata**: Additional context about the interaction

### API Endpoints

The server provides RESTful API endpoints for accessing analytics data:

```bash
# Health check
GET /api/health

# Get questions with filtering
GET /api/questions?limit=100&user_id=user123&start_date=2024-01-01

# Get analytics data
GET /api/analytics?days=30

# Get daily statistics
GET /api/analytics/daily?date=2024-01-15

# Get system statistics
GET /api/stats

# Export questions data
GET /api/export/questions?format=csv&start_date=2024-01-01

# Store a question (used by UI)
POST /api/questions
```

### Analytics Dashboard

A web-based dashboard provides real-time visualization of system usage:

```bash
# Start the analytics dashboard
python serve_analytics.py --port 8080
```

**Features:**
- Real-time statistics (questions, success rate, response times)
- Interactive charts showing daily usage patterns
- Recent questions table with status and performance metrics
- Data export functionality (CSV format)
- Auto-refresh every 30 seconds

### Slack Integration

Configure Slack notifications by setting the `SLACK_WEBHOOK_URL` environment variable:

```bash
# Add to config.env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Available Notifications:**
- **Question Notifications**: Real-time alerts for new questions
- **Daily Analytics Reports**: Automated daily summaries
- **Error Alerts**: System error notifications
- **System Status**: Startup/shutdown notifications

**Slack API Endpoints:**
```bash
# Test Slack integration
POST /api/slack/test

# Send analytics report to Slack
POST /api/slack/analytics?days=7
```

### Database Schema

The SQLite database contains two main tables:

**questions table:**
- `id`: Primary key
- `question`: User's question text
- `user_id`: User identifier
- `session_id`: Session identifier
- `timestamp`: When the question was asked
- `response_time_ms`: Response time in milliseconds
- `tools_called`: JSON array of tools used
- `response_length`: Length of the response
- `success`: Whether the request succeeded
- `error_message`: Error details if failed
- `metadata`: Additional JSON metadata

**analytics table:**
- `id`: Primary key
- `date`: Date of the analytics
- `total_questions`: Total questions for the day
- `successful_questions`: Successful questions count
- `avg_response_time_ms`: Average response time
- `unique_users`: Number of unique users
- `created_at`: When the record was created
- `updated_at`: When the record was last updated

## Configuration

### Environment Variables

- `MCP_SERVER_PORT`: Port for the MCP server (default: 9000)
- `PRIDE_API_BASE_URL`: PRIDE Archive API base URL (default: https://www.ebi.ac.uk/pride/ws/archive/v3)

### Settings

Configuration is managed through `config/settings.py`. Key settings include:

- API endpoints and timeouts
- Logging configuration
- Server settings

## Project Structure

```
pride-mcp-server/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration settings
├── servers/
│   ├── __init__.py
│   └── pride_mcp_server.py  # Main MCP server implementation
├── tools/
│   ├── __init__.py
│   └── pride_archive_public_api.py  # PRIDE API integration
├── utils/
│   ├── __init__.py
│   └── logging.py           # Logging utilities
├── mcp_client_tools/        # Professional UI and client tools
├── database.py              # SQLite database management
├── slack_integration.py     # Slack notifications
├── api_endpoints.py         # REST API endpoints
├── analytics_dashboard.html # Web analytics dashboard
├── serve_analytics.py       # Analytics dashboard server
├── main.py                  # Server entry point
├── server.py               # Enhanced server with API endpoints
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Development

### Setup Development Environment

```bash
# Install in development mode
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .
```

### Adding New Tools

1. Define the tool in `servers/pride_mcp_server.py`
2. Implement the tool logic in `tools/pride_archive_public_api.py`
3. Update the tool schema and documentation

## API Reference

### PRIDE Archive API

The server integrates with the PRIDE Archive REST API:

- **Base URL**: https://www.ebi.ac.uk/pride/ws/archive/v3
- **Documentation**: https://www.ebi.ac.uk/pride/ws/archive/v3/docs

### MCP Protocol

The server implements the Model Context Protocol:

- **Specification**: https://modelcontextprotocol.io/
- **Tools**: JSON-RPC 2.0 over HTTP

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- PRIDE Archive team for providing the proteomics data and API
- MCP community for the protocol specification
- Contributors and maintainers

## Support

- Documentation: [GitHub Wiki](https://github.com/yourusername/pride-mcp-server/wiki)
- Issues: [GitHub Issues](https://github.com/yourusername/pride-mcp-server/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/pride-mcp-server/discussions)