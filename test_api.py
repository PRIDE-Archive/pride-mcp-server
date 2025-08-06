import httpx
import asyncio
import os

async def test_pride_api():
    # Get proxy configuration from environment
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
    print(f"Using proxy: {proxy}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0, proxy=proxy) as client:
            url = "https://www.ebi.ac.uk/pride/ws/archive/v2/projects?keyword=breast%20cancer&pageSize=3"
            print(f"Testing URL: {url}")
            
            response = await client.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Found {len(data)} projects")
                if data:
                    print(f"First project: {data[0].get('accession', 'N/A')} - {data[0].get('title', 'N/A')[:50]}...")
            else:
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_pride_api()) 