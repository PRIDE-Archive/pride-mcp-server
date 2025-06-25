from server import mcp

# -----------------------------------------
# Import tools so they get registered via decorators

import tools.pride_archive_public_api
# -----------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http")