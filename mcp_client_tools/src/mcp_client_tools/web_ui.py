"""
Simple web UI for testing MCP client tools.
"""

import json
import logging
from typing import Dict, Any
from .client import MCPClient

logger = logging.getLogger(__name__)


class MCPWebUI:
    """Simple web UI for testing MCP client tools."""
    
    def __init__(self, mcp_server_url: str):
        """Initialize the web UI.
        
        Args:
            mcp_server_url: The URL of the MCP server
        """
        self.client = MCPClient(mcp_server_url)
        self.server_url = mcp_server_url
    
    def test_get_facets(self) -> Dict[str, Any]:
        """Test the get_pride_facets tool.
        
        Returns:
            The response from the facets tool
        """
        try:
            logger.info("Testing get_pride_facets tool...")
            result = self.client.call_tool("get_pride_facets", {})
            logger.info("✅ get_pride_facets test successful")
            return result
        except Exception as e:
            logger.error(f"❌ get_pride_facets test failed: {e}")
            return {"error": str(e)}
    
    def test_search_projects(self, keyword: str, facets: list = None) -> Dict[str, Any]:
        """Test the search_pride_projects tool.
        
        Args:
            keyword: The search keyword
            facets: Optional list of facet filters
            
        Returns:
            The response from the search tool
        """
        try:
            logger.info(f"Testing search_pride_projects tool with keyword: {keyword}")
            parameters = {"keyword": keyword}
            if facets:
                parameters["facets"] = facets
            
            result = self.client.call_tool("search_pride_projects", parameters)
            logger.info("✅ search_pride_projects test successful")
            return result
        except Exception as e:
            logger.error(f"❌ search_pride_projects test failed: {e}")
            return {"error": str(e)}
    
    def run_demo(self) -> Dict[str, Any]:
        """Run a demo of the MCP client tools.
        
        Returns:
            Dictionary with demo results
        """
        logger.info("🚀 Starting MCP Client Tools Demo...")
        
        results = {
            "server_url": self.server_url,
            "tests": {}
        }
        
        # Test 1: Get facets
        logger.info("📋 Test 1: Getting PRIDE facets...")
        facets_result = self.test_get_facets()
        results["tests"]["get_facets"] = facets_result
        
        # Test 2: Search for projects
        logger.info("🔍 Test 2: Searching for projects...")
        search_result = self.test_search_projects("cancer")
        results["tests"]["search_projects"] = search_result
        
        logger.info("✅ Demo completed!")
        return results


def main():
    """Main function for running the web UI demo."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Client Tools Web UI")
    parser.add_argument("--server-url", default="http://127.0.0.1:9000", 
                       help="MCP server URL")
    parser.add_argument("--demo", action="store_true", 
                       help="Run demo tests")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create web UI
    ui = MCPWebUI(args.server_url)
    
    if args.demo:
        # Run demo
        results = ui.run_demo()
        print("\n" + "="*50)
        print("MCP CLIENT TOOLS DEMO RESULTS")
        print("="*50)
        print(f"Server URL: {results['server_url']}")
        print("\nTest Results:")
        for test_name, result in results["tests"].items():
            print(f"\n{test_name}:")
            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                print(f"  ✅ Success: {len(str(result))} characters of data")
    else:
        print("MCP Client Tools Web UI")
        print(f"Server URL: {args.server_url}")
        print("\nUse --demo to run demonstration tests")


if __name__ == "__main__":
    main() 