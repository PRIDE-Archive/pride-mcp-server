from tools.pride_archive_public_api import mcp
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# Get the Starlette app from the MCP instance
app = mcp.streamable_http_app()

# Add CORS middleware to allow requests from the UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:9090", "http://localhost:9090", "http://127.0.0.1:8080", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    print("🚀 Starting PRIDE MCP Server...")
    print("   Server URL: http://127.0.0.1:9000")
    print("   MCP Endpoint: http://127.0.0.1:9000/mcp/")
    print("   Log Level: INFO")
    uvicorn.run(app, host="127.0.0.1", port=9000, log_level="info", access_log=True) 