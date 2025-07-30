"""
MCP Client Tools - A client library for interacting with MCP servers.

This package provides tools for connecting to and interacting with
Model Context Protocol (MCP) servers, with specific support for
PRIDE Archive proteomics data.
"""

__version__ = "0.1.0" # Define your module version

# Optionally, expose the main classes/definitions for easier import
from .client import MCPClient
from .tools import PRIDE_EBI_TOOLS
from .web_ui import MCPWebUI
from .conversational_ui import run_conversational_ui
from .ai_conversational_ui import run_ai_conversational_ui 