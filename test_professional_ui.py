#!/usr/bin/env python3
"""
Test script for the new Professional UI.
"""

import sys
import os
from pathlib import Path

# Add the client module to Python path
client_dir = Path("mcp_client_tools")
if client_dir.exists():
    sys.path.insert(0, str(client_dir / "src"))

try:
    from mcp_client_tools.professional_ui import run_professional_ui
    print("🚀 Starting Professional UI...")
    run_professional_ui("http://127.0.0.1:9000", 9090, "127.0.0.1")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the project root directory and the mcp_client_tools module is available.")
except Exception as e:
    print(f"❌ Error: {e}") 