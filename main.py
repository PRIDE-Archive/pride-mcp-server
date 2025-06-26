import argparse
import uvicorn
from server import app

if __name__ == "__main__":
    # Use argparse to get host and port from command line arguments
    parser = argparse.ArgumentParser(description="Run MCP server with FastAPI")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host IP address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")