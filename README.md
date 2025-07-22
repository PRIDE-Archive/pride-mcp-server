# 🧬 MCP PRIDE Archive Search Server with Gemini Pro Integration

This project implements a **Model Context Protocol (MCP)**-compliant API server that exposes tools to search the [PRIDE Archive](https://www.ebi.ac.uk/pride/), a major repository for proteomics data. It allows AI models (such as Claude, Gemini, or other MCP-compatible LLMs) to interact with proteomics datasets programmatically using structured function calling, with enhanced AI-powered analysis capabilities.

---

## 🚀 Features

- ✅ MCP Server powered by `FastMCP`
- 🔍 PRIDE Archive Search Tool to query datasets by keyword, submission date, popularity, etc.
- 🤖 **Gemini Pro AI Integration** for enhanced data analysis and insights
- 🧠 AI-powered proteomics data analysis and research suggestions
- 🤖 AI-friendly tools for biomedical and proteomics-related research
- ⚡ Supports both `http` (SSE) and `stdio` connection modes
- 🛠️ Easily extendable with additional tools

---

## 📦 Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/PRIDE-Archive/pride_mcp_server.git
cd pride_mcp_server

uv venv
source .venv/bin/activate
uv sync
```

## 🔑 Gemini Pro API Setup

To enable AI-powered analysis features, you'll need a Gemini Pro API key:

1. **Get your API key** from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Set the environment variable**:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```
   
   Or create a `.env` file:
   ```bash
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-1.5-pro  # Optional, defaults to gemini-1.5-pro
   ENABLE_GEMINI=true           # Optional, defaults to true
   ```

The server will work without the API key, but AI analysis features will be disabled.

## 👨‍💻 Usage

### Quick Start (Recommended)
Start both the MCP server and web UI with one command:

```bash
./start_with_ui.sh
```

This will:
- Start the MCP server on port 9000
- Start the web UI on port 8080
- Open your browser to http://127.0.0.1:8080

### Manual Start
Start just the MCP server:

```bash
./start_server.sh
```

Or start manually:

```bash
uv run main.py
```

## 🔧 Tool APIs

### fetch_projects(...)
Fetches proteomics datasets from the PRIDE Archive database.

**Use this when:**
- Searching for proteomics research data
- Mass spectrometry dataset queries
- Biomedical dataset exploration (e.g., cancer-related)
- Finding popular or specific proteomics projects

### get_project_details(project_accession)
Retrieves detailed information about a specific PRIDE project.

### get_project_files(project_accession, file_type)
Retrieves file information for a specific PRIDE project.

### analyze_with_gemini(data, analysis_type, context)
**NEW: AI-powered analysis using Gemini Pro**

Analyzes data using Google's Gemini Pro AI model for enhanced insights.

**Use this when:**
- You want AI-powered analysis of proteomics data
- Need insights about research findings
- Want to understand complex biological data
- Need suggestions for research directions

**Parameters:**
- `data`: The data to analyze (JSON string, text, or structured data)
- `analysis_type`: Type of analysis ('general', 'proteomics', 'research', 'biological')
- `context`: Additional context or background information


##  🤝 Integration with LLMs

This server works with any LLM that supports Model Context Protocol, including:

- Anthropic Claude
- Google Gemini
- Open-source MCP clients 
- Custom RAG pipelines

### Enhanced AI Capabilities

With Gemini Pro integration, the server provides:
- **AI-powered data analysis** of proteomics datasets
- **Research suggestions** based on project metadata
- **Biological insights** from experimental data
- **Enhanced search result interpretation**

## 🌐 Web UI

A modern web interface is included for easy testing and interaction:

- **Beautiful, responsive design** with Tailwind CSS
- **Real-time tool testing** with live results
- **Gemini Pro integration** with AI analysis features
- **Interactive forms** for all MCP tools
- **Status indicators** for server and AI service health

### Web UI Features
- Search PRIDE projects with filters
- Get detailed project information
- AI-powered data analysis with Gemini Pro
- Real-time results display
- Example data loading
- Error handling and status feedback

## 🧠 Architecture Overview

```sql
+---------------------+       Tool Calls        +-----------------------------+
|  Claude / Gemini AI |  <--------------------> | MCP PRIDE API Server        |
+---------------------+                         | - search_archive_tool()     |
                                                | - server_status()           |
                                                +-----------------------------+
                                                           |
                                                           v
                                              +---------------------------+
                                              | PRIDE Archive REST API    |
                                              | (https://www.ebi.ac.uk    |
                                              |   /pride/ws/archive/      |
                                              |  v3/search/projects)      |
                                              +---------------------------+
```

## 📝 License

MIT License. See LICENSE for details.