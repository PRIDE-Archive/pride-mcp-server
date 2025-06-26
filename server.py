import contextlib
from fastapi import FastAPI
from servers.pride_mcp_server import mcp as pride_mcp # Import the mcp instance from echo.py

# Import tools to register them with the MCP server
import tools

# Create a combined lifespan to manage both session managers
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(pride_mcp.session_manager.run())
        yield

app = FastAPI(lifespan=lifespan)
app.mount("/pride", pride_mcp.streamable_http_app())