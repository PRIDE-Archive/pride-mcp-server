#!/usr/bin/env python3
"""
Simple Web UI for testing PRIDE MCP Server with Gemini Pro integration.
"""

import asyncio
import json
import os
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="PRIDE MCP Server UI", description="Web UI for testing MCP tools with Gemini Pro")

# Mount static files and templates
templates = Jinja2Templates(directory="templates")

# MCP Server configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:9000")

class MCPClient:
    """Simple MCP client for testing tools."""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.client = httpx.AsyncClient()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        try:
            # For simplicity, we'll use a direct HTTP call to the MCP server
            # In a real implementation, you'd use the proper MCP protocol
            response = await self.client.post(
                f"{self.server_url}/tools/{tool_name}",
                json=arguments,
                timeout=30.0
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Global MCP client
mcp_client = MCPClient(MCP_SERVER_URL)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with tool selection."""
    return templates.TemplateResponse("ui_test.html", {
        "request": request,
        "gemini_enabled": bool(os.getenv("GEMINI_API_KEY")),
        "mcp_server_url": MCP_SERVER_URL
    })

@app.post("/api/search")
async def search_projects(
    keyword: str = Form(...),
    page_size: int = Form(5),
    page: int = Form(0),
    sort_direction: str = Form("DESC"),
    sort_fields: str = Form("downloadCount"),
    filters: str = Form("")
):
    """Search for PRIDE projects."""
    try:
        # Import the tool directly for testing
        from tools.pride_archive_public_api import fetch_projects
        
        result = await fetch_projects(
            keyword=keyword,
            page_size=page_size,
            page=page,
            sort_direction=sort_direction,
            sort_fields=sort_fields,
            filters=filters
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/project-details")
async def get_project_details(project_accession: str = Form(...)):
    """Get project details."""
    try:
        from tools.pride_archive_public_api import get_project_details
        
        result = await get_project_details(project_accession)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/analyze-gemini")
async def analyze_with_gemini(
    data: str = Form(...),
    analysis_type: str = Form("general"),
    context: str = Form("")
):
    """Analyze data with Gemini Pro."""
    try:
        from tools.pride_archive_public_api import analyze_with_gemini
        
        result = await analyze_with_gemini(
            data=data,
            analysis_type=analysis_type,
            context=context
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/ask-question")
async def ask_question(question: str = Form(...)):
    """Ask natural language questions about proteomics data."""
    try:
        print(f"🌐 Web UI: Received question: {question}")
        
        # Import the individual tools
        from tools.pride_archive_public_api import get_pride_facets, fetch_projects
        
        print(f"🌐 Web UI: Getting available facets...")
        # Step 1: Get available facets to understand what filters are available
        facets_result = await get_pride_facets(facet_page_size=100, facet_page=0)
        
        if "error" in facets_result:
            return {
                "success": False,
                "error": facets_result["error"],
                "reasoning": "Failed to get available filters"
            }
        
        facets = facets_result.get("data", {})
        print(f"🌐 Web UI: Got {len(facets)} facet categories")
        
        # Step 2: Simple keyword extraction and filter mapping
        question_lower = question.lower()
        keywords = []
        filters = []
        
        # Simple keyword extraction - let the LLM handle filter mapping
        # Extract keywords (avoid filter terms)
        words = question_lower.split()
        stop_words = {"find", "search", "for", "studies", "projects", "on", "using", "proteomics"}
        
        for word in words:
            if word not in stop_words and len(word) > 2:
                keywords.append(word)
        
        # Use keywords for search
        search_keyword = " ".join(keywords[:2]) if keywords else ""
        filters_string = ",".join(filters) if filters else ""
        
        print(f"🌐 Web UI: Search parameters - Keywords: '{search_keyword}', Filters: '{filters_string}'")
        
        # Step 3: Perform the search
        search_result = await fetch_projects(
            keyword=search_keyword,
            page_size=25,
            page=0,
            sort_direction="DESC",
            sort_fields="downloadCount",
            filters=filters_string
        )
        
        result = {
            "reasoning": f"Processed question using facet data. Found {len(facets)} facet categories. LLM should use get_pride_facets to identify appropriate filters.",
            "highlights": {
                "question": question,
                "extracted_keywords": search_keyword,
                "extracted_filters": filters_string,
                "projects_found": len(search_result.get("data", [])),
                "facet_categories_available": len(facets)
            },
            "data": search_result.get("data", []),
            "search_criteria": search_result.get("search_criteria", {}),
            "endpoint_url": search_result.get("endpoint_url", ""),
            "parameters": search_result.get("parameters", {}),
            "available_facets": facets
        }
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        print(f"🌐 Web UI: Exception occurred: {str(e)}")
        import traceback
        print(f"🌐 Web UI: Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "gemini_enabled": bool(os.getenv("GEMINI_API_KEY")),
        "mcp_server_url": MCP_SERVER_URL
    }

if __name__ == "__main__":
    import sys
    
    # Get port from command line argument or use default
    port = 9090
    if len(sys.argv) > 2 and sys.argv[1] == "--port":
        port = int(sys.argv[2])
    
    print("🌐 Starting PRIDE MCP Server Web UI...")
    print(f"   MCP Server URL: {MCP_SERVER_URL}")
    print(f"   Gemini Enabled: {bool(os.getenv('GEMINI_API_KEY'))}")
    print(f"   Web UI: http://127.0.0.1:{port}")
    
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info") 