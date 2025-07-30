import argparse
import uvicorn
from server import app
from config.settings import settings

if __name__ == "__main__":
    # Use argparse to get host and port from command line arguments
    parser = argparse.ArgumentParser(description="Run MCP server with AI integration")
    parser.add_argument("--host", type=str, default=settings.HOST, help="Host IP address")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Port number")
    args = parser.parse_args()

    # Validate AI configuration
    print("🚀 Starting PRIDE MCP Server with AI integration...")
    ai_config = settings.validate_ai_config()
    
    if ai_config["enabled"] and ai_config["valid"]:
        print(f"✅ {ai_config['message']}")
    else:
        print(f"⚠️  AI integration disabled - {ai_config['message']}")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")