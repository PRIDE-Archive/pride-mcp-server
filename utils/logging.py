"""
Logging configuration for MCP PRIDE Archive Search.
"""
import logging
from rich.logging import RichHandler

def setup_logging():
    """Configure and set up logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="| %(levelname)-8s | %(name)s | %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[RichHandler(rich_tracebacks=True)],
        force=True  # This is the fix that overrides uvicorn & third-party loggers
    )

    logger = logging.getLogger("pride_mcp_server")
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.INFO)  # Changed from WARNING to INFO
    logging.getLogger("mcp_client_tools").setLevel(logging.INFO)
    
    return logger

# Create the logger instance for import by other modules
logger = setup_logging() 