import sys
import os
sys.path.append('/tmp')

from pride_archive_public_api import fetch_projects, get_pride_facets
import asyncio

async def test_fixed_api():
    print("Testing fixed PRIDE API functions...")
    
    # Test fetch_projects
    print("\n1. Testing fetch_projects with 'breast' keyword:")
    try:
        result = await fetch_projects("breast", page_size=3)
        print(f"Status: {'Success' if 'error' not in result else 'Failed'}")
        if 'error' not in result:
            print(f"Found {len(result['data'])} projects")
            print(f"Total projects: {result['highlights']['total_projects']}")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test get_pride_facets
    print("\n2. Testing get_pride_facets:")
    try:
        result = await get_pride_facets(facet_page_size=10)
        print(f"Status: {'Success' if 'error' not in result else 'Failed'}")
        if 'error' not in result:
            print(f"Retrieved {result['highlights']['total_facets']} facet categories")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_fixed_api()) 