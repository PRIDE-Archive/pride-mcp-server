from tools.pride_archive_public_api import mcp
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import uvicorn
import logging
from database import db
from slack_integration import slack

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the Starlette app from the MCP instance
mcp_app = mcp.streamable_http_app()

# Create a new FastAPI app that includes both MCP and API endpoints
app = FastAPI(
    title="PRIDE MCP Server",
    description="Model Context Protocol server for PRIDE Archive proteomics data with analytics",
    version="2.0.0"
)

# Include the MCP routes
app.mount("/mcp", mcp_app)

# Include the API endpoints with custom prefix for EBI integration
from api_endpoints import api_router
app.include_router(api_router, prefix="/api")

# Add CORS middleware to allow requests from the UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:9090", 
        "http://localhost:9090", 
        "http://127.0.0.1:8080", 
        "http://localhost:8080",
        "https://www.ebi.ac.uk",  # EBI main domain
        "https://*.ebi.ac.uk"     # EBI subdomains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("🚀 Starting PRIDE MCP Server...")
    
    # Initialize database
    try:
        db.init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Send startup notification to Slack
    try:
        await slack.send_system_status("online", {
            "server_url": "http://127.0.0.1:9000",
            "mcp_endpoint": "http://127.0.0.1:9000/mcp/",
            "api_endpoint": "http://127.0.0.1:9000/api/"
        })
    except Exception as e:
        logger.warning(f"⚠️ Failed to send Slack startup notification: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down PRIDE MCP Server...")
    
    # Send shutdown notification to Slack
    try:
        await slack.send_system_status("offline")
    except Exception as e:
        logger.warning(f"⚠️ Failed to send Slack shutdown notification: {e}")

@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "service": "PRIDE MCP Server",
        "version": "2.0.0",
        "endpoints": {
            "mcp": "/mcp/",
            "api": "/api/",
            "health": "/api/health",
            "analytics": "/api/analytics",
            "questions": "/api/questions",
            "stats": "/api/stats"
        },
        "documentation": "/docs"
    }

if __name__ == "__main__":
    print("🚀 Starting PRIDE MCP Server...")
    print("   Server URL: http://127.0.0.1:9000")
    print("   MCP Endpoint: http://127.0.0.1:9000/mcp/")
    print("   API Endpoint: http://127.0.0.1:9000/api/")
    print("   Documentation: http://127.0.0.1:9000/docs")
    print("   Log Level: INFO")
    uvicorn.run(app, host="127.0.0.1", port=9000, log_level="info", access_log=True) 