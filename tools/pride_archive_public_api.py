from servers.pride_mcp_server import mcp
import httpx

"""
PRIDE archive search service implementation.
"""
@mcp.tool()
async def fetch_projects(
        keyword: str,
        page_size: int,
        page: int,
        sort_direction: str,
        sort_fields: str,
):
    """
Fetches proteomics datasets from the PRIDE Archive database.
Use this function when:
- User is looking for proteomics research data
- Questions involve mass spectrometry datasets
- Queries about biological/biomedical datasets (especially cancer-related)
- User wants to find popular or specific proteomics projects

The function supports filtering by keyword, sorting by submissionDate,
and pagination for browsing results.

Args:
        keyword: The keyword for searching projects (e.g., 'Cancer').
        page_size: The number of results per page.
        page: The page number for pagination. Page starts with 0 and default value is 0
        sort_direction: The direction for sorting results ('ASC' or 'DESC').Default is DESC
        sort_fields: The fields to sort by (e.g., 'submissionDate','downloadCount').

Returns:
        A list of project accessions if successful, otherwise a dictionary with an error message.
"""
    url = "https://www.ebi.ac.uk/pride/ws/archive/v3/search/projects"
    params = {
        "keyword": keyword,
        "pageSize": page_size,
        "page": page,
        "sortDirection": sort_direction,
        "sortFields": sort_fields
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            accessions = [entry["accession"] for entry in data]
            print(accessions)
            return accessions
        else:
            return {"error": f"Request failed with status code {response.status_code}"}

@mcp.tool()
async def get_project_details(project_accession: str):
    """
    Retrieves detailed information about a specific PRIDE project.
    
    Use this function when:
    - User wants detailed information about a specific proteomics project
    - Need to understand project metadata, publication info, or experimental details
    - Want to get project title, description, submission date, and other metadata
    
    Args:
        project_accession: The PRIDE project accession (e.g., 'PXD000001')
        
    Returns:
        Detailed project information including title, description, submission date, 
        publication info, and experimental metadata.
    """
    url = f"https://www.ebi.ac.uk/pride/ws/archive/v3/projects/{project_accession}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Request failed with status code {response.status_code}"}

@mcp.tool()
async def get_project_files(project_accession: str, file_type: str = None):
    """
    Retrieves file information for a specific PRIDE project.
    
    Use this function when:
    - User wants to see what files are available in a project
    - Need to understand the data files, spectra, or identification results
    - Want to filter files by type (e.g., mzML, mzIdentML, etc.)
    
    Args:
        project_accession: The PRIDE project accession (e.g., 'PXD000001')
        file_type: Optional filter for specific file types (e.g., 'mzML', 'mzIdentML', 'fasta')
        
    Returns:
        List of files in the project with their metadata, file types, and download links.
    """
    url = f"https://www.ebi.ac.uk/pride/ws/archive/v3/projects/{project_accession}/files"
    params = {}
    if file_type:
        params["fileType"] = file_type
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Request failed with status code {response.status_code}"}


@mcp.tool()
async def search_projects_by_organism(organism: str, page_size: int = 100, page: int = 0):
    """
    Searches for PRIDE projects by organism/species.
    
    Use this function when:
    - User wants to find proteomics data from specific organisms
    - Need to analyze data from model organisms or specific species
    - Want to compare proteomes across different organisms
    
    Args:
        organism: Organism name (e.g., 'Homo sapiens', 'Mus musculus', 'Escherichia coli')
        page_size: Number of results per page (default: 100)
        page: Page number for pagination (default: 0)
        
    Returns:
        List of projects related to the specified organism.
    """
    url = "https://www.ebi.ac.uk/pride/ws/archive/v3/search/projects"
    params = {
        "organism": organism,
        "pageSize": page_size,
        "page": page
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": f"Request failed with status code {response.status_code}"}