"""
MCP Client implementation for interacting with MCP servers.

This module provides the MCPClient class for making requests to
Model Context Protocol (MCP) servers.
"""

import asyncio
import json
import logging
import httpx
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MCPClient:
    """
    A client for interacting with a Model Context Protocol (MCP) server.
    This client is designed to call tools exposed by the MCP server.
    """
    def __init__(self, mcp_server_url: str, timeout: int = 60):
        """
        Initializes the MCPClient.

        Args:
            mcp_server_url (str): The base URL of your MCP server (e.g., "http://localhost:9000").
            timeout (int): The request timeout in seconds.
        """
        if not mcp_server_url:
            raise ValueError("MCP_SERVER_URL must be provided.")
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.timeout = timeout
        logger.info(f"MCPClient initialized for server: {self.mcp_server_url}")



    async def call_tool_async(self, tool_name: str, parameters: dict) -> Dict[str, Any]:
        """
        Calls a specific tool on the MCP server asynchronously.

        Args:
            tool_name (str): The name of the tool to call (as defined by your MCP server).
            parameters (dict): A dictionary of parameters for the tool call.

        Returns:
            dict: The JSON response from the MCP server.

        Raises:
            ConnectionError: If there's a network issue or timeout.
            ValueError: If the MCP server returns an invalid response.
        """
        try:
            logger.info(f"Attempting to call MCP tool '{tool_name}' with parameters: {json.dumps(parameters)}")
            
            # Use httpx directly with correct headers for MCP server
            headers = {
                "Accept": "text/event-stream, application/json",
                "Content-Type": "application/json"
            }
            
            # MCP JSON-RPC request format
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.mcp_server_url}/mcp/",
                    json=mcp_request,
                    headers=headers,
                    timeout=self.timeout
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response headers: {response.headers}")
                
                if response.status_code == 200:
                    # Parse SSE response
                    content = response.text
                    logger.info(f"Raw response length: {len(content)} characters")
                    
                    # Extract JSON from SSE stream
                    lines = content.strip().split('\n')
                    logger.info(f"Found {len(lines)} lines in response")
                    
                    for line in lines:
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            if data.strip():
                                try:
                                    result = json.loads(data)
                                    logger.info(f"Successfully parsed result for tool '{tool_name}'")
                                    return result
                                except json.JSONDecodeError as e:
                                    logger.warning(f"Failed to parse JSON from line: {e}")
                                    continue
                    
                    logger.error(f"No valid JSON found in response for tool '{tool_name}'")
                    return {"error": "No valid JSON found in response", "content": content[:200]}
                else:
                    logger.error(f"HTTP error: {response.status_code} - {response.text}")
                    raise ConnectionError(f"HTTP {response.status_code}: {response.text}")
            
        except Exception as e:
            logger.error(f"Error calling MCP tool '{tool_name}': {e}")
            raise ConnectionError(f"Failed to call MCP tool '{tool_name}': {e}")

    def call_tool(self, tool_name: str, parameters: dict) -> Dict[str, Any]:
        """
        Calls a specific tool on the MCP server synchronously.

        Args:
            tool_name (str): The name of the tool to call (as defined by your MCP server).
            parameters (dict): A dictionary of parameters for the tool call.

        Returns:
            dict: The JSON response from the MCP server.

        Raises:
            ConnectionError: If there's a network issue or timeout.
            ValueError: If the MCP server returns an invalid response.
        """
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, use asyncio.create_task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.call_tool_async(tool_name, parameters))
                    return future.result()
            except RuntimeError:
                # No event loop running, create a new one
                return asyncio.run(self.call_tool_async(tool_name, parameters))
        except Exception as e:
            logger.error(f"Error in synchronous tool call '{tool_name}': {e}")
            raise

    async def list_tools_async(self) -> List[Dict[str, Any]]:
        """
        Lists all available tools from the MCP server asynchronously.

        Returns:
            List[Dict[str, Any]]: List of available tools.
        """
        try:
            # Use httpx directly with correct headers for MCP server
            headers = {
                "Accept": "text/event-stream, application/json",
                "Content-Type": "application/json"
            }
            
            # MCP JSON-RPC request format for listing tools
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.mcp_server_url}/mcp/",
                    json=mcp_request,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    # Parse SSE response
                    content = response.text
                    lines = content.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            if data.strip():
                                try:
                                    result = json.loads(data)
                                    if 'result' in result and 'tools' in result['result']:
                                        return result['result']['tools']
                                    return result
                                except json.JSONDecodeError:
                                    continue
                    
                    return []
                else:
                    logger.error(f"HTTP error: {response.status_code} - {response.text}")
                    raise ConnectionError(f"HTTP {response.status_code}: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error listing MCP tools: {e}")
            raise ConnectionError(f"Failed to list MCP tools: {e}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lists all available tools from the MCP server synchronously.

        Returns:
            List[Dict[str, Any]]: List of available tools.
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.list_tools_async())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in synchronous tool listing: {e}")
            raise

 