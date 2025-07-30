"""
PRIDE EBI Tools definition for MCP server.

This module defines the tools available in the PRIDE Archive MCP server.
"""

# src/mcp_client_tools/tools.py

# These tool definitions are crucial for Gemini's function calling.
# They describe the capabilities of your MCP server to the LLM.

PRIDE_EBI_TOOLS = [
    {
        "name": "get_pride_facets",
        "description": "Retrieves the available facets (categories for filtering) for PRIDE EBI projects. This should be called first by the AI to understand what filters can be applied for subsequent searches, for example, to tell the user what organisms or instruments are available.",
        "parameters": {
            "type": "object",
            "properties": {
                "facet_page_size": {
                    "type": "integer",
                    "description": "Number of facet values to retrieve per page (default: 100)",
                    "default": 100
                },
                "facet_page": {
                    "type": "integer", 
                    "description": "Page number for pagination (default: 0)",
                    "default": 0
                }
            },
            "required": []
        }
    },
    {
        "name": "fetch_projects",
        "description": "Search for proteomics projects in the PRIDE Archive database based on keywords and various filtering options. Always consider calling 'get_pride_facets' first if you need to suggest or validate filter values to the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "The keyword for searching projects (e.g., 'cancer', 'proteomics', 'phosphorylation'). This is a mandatory parameter for the search."
                },
                "page_size": {
                    "type": "integer",
                    "description": "The number of results per page (default: 25)",
                    "default": 25
                },
                "page": {
                    "type": "integer",
                    "description": "The page number for pagination (default: 0)",
                    "default": 0
                },
                "sort_direction": {
                    "type": "string",
                    "description": "The direction for sorting results ('ASC' or 'DESC', default: DESC)",
                    "default": "DESC"
                },
                "sort_fields": {
                    "type": "string",
                    "description": "The fields to sort by (default: 'downloadCount')",
                    "default": "downloadCount"
                },
                "filters": {
                    "type": "string",
                    "description": "Comma-separated filters using exact values from get_pride_facets (default: empty)"
                }
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "get_project_details",
        "description": "Retrieves detailed information about a specific PRIDE project.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_accession": {
                    "type": "string",
                    "description": "The PRIDE project accession (e.g., 'PXD000001')"
                }
            },
            "required": ["project_accession"]
        }
    },
    {
        "name": "get_project_files",
        "description": "Retrieves file information for a specific PRIDE project.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_accession": {
                    "type": "string",
                    "description": "The PRIDE project accession (e.g., 'PXD000001')"
                },
                "file_type": {
                    "type": "string",
                    "description": "Optional filter for specific file types (e.g., 'mzML', 'mzIdentML', 'fasta')"
                }
            },
            "required": ["project_accession"]
        }
    }
] 