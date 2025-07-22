import argparse
import uvicorn
from server import app
from config.settings import settings

if __name__ == "__main__":
    # Use argparse to get host and port from command line arguments
    parser = argparse.ArgumentParser(description="Run MCP server with FastAPI")
    parser.add_argument("--host", type=str, default=settings.HOST, help="Host IP address")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Port number")
    args = parser.parse_args()

    # Validate Gemini configuration
    print("🚀 Starting PRIDE MCP Server with Gemini Pro integration...")
    settings.validate_gemini_config()
    
    if settings.ENABLE_GEMINI and settings.GEMINI_API_KEY:
        print("✅ Gemini Pro integration enabled")
    else:
        print("⚠️  Gemini Pro integration disabled - set GEMINI_API_KEY to enable")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")