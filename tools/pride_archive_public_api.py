from mcp.server.fastmcp import FastMCP
import httpx
import json
import os
from typing import Dict, Any, List

# Create MCP instance for tools
mcp = FastMCP(name="pride_mcp_server", stateless_http=True)

@mcp.tool()
async def get_pride_facets(facet_page_size: int = 100, facet_page: int = 0, keyword: str = None):
    """
    Fetch available filter values from the PRIDE Archive facet endpoint.
    
    Args:
        facet_page_size: Number of facet values to retrieve per page (default: 100)
        facet_page: Page number for pagination (default: 0)
        keyword: Optional keyword to filter facets (default: None)
        
    Returns:
        Dictionary containing all available filter values organized by category.
    """
    url = "https://www.ebi.ac.uk/pride/ws/archive/v3/facet/projects"
    params = {
        "facetPageSize": facet_page_size,
        "facetPage": facet_page
    }
    
    # Add keyword filter if provided
    if keyword:
        params["keyword"] = keyword
    
    try:
        # Get proxy configuration from environment
        proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
        
        # Only use proxy if it's configured
        client_kwargs = {"timeout": 10.0}
        if proxy:
            client_kwargs["proxy"] = proxy
        
        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract and organize the facet data
                facets = {
                    "organisms": data.get("organisms", {}),
                    "instruments": data.get("instruments", {}),
                    "experimentTypes": data.get("experimentTypes", {}),
                    "keywords": data.get("keywords", {}),
                    "diseases": data.get("diseases", {}),
                    "quantificationMethods": data.get("quantificationMethods", {}),
                    "softwares": data.get("softwares", {}),
                    "projectTags": data.get("projectTags", {}),
                    "submissionDate": data.get("submissionDate", {}),
                    "otherOmicsLinks": data.get("otherOmicsLinks", {})
                }
                
                # Create highlights for the response
                highlights = {
                    "total_facets": len(facets),
                    "organisms_count": len(facets["organisms"]),
                    "instruments_count": len(facets["instruments"]),
                    "experiment_types_count": len(facets["experimentTypes"]),
                    "keywords_count": len(facets["keywords"]),
                    "diseases_count": len(facets["diseases"]),
                    "top_organisms": dict(list(facets["organisms"].items())[:5]),
                    "top_experiment_types": dict(list(facets["experimentTypes"].items())[:5]),
                    "top_keywords": dict(list(facets["keywords"].items())[:5])
                }
                
                result = {
                    "reasoning": f"Successfully retrieved {len(facets)} facet categories from PRIDE Archive.",
                    "highlights": highlights,
                    "data": facets,
                    "endpoint_url": url,
                    "parameters": params
                }
                
                print(f"📊 PRIDE Facets Retrieved from: {url}")
                print(f"   🧬 Organisms: {highlights['organisms_count']} unique values")
                print(f"   🔬 Instruments: {highlights['instruments_count']} unique values")
                print(f"   🧪 Experiment Types: {highlights['experiment_types_count']} unique values")
                print(f"   🏷️  Keywords: {highlights['keywords_count']} unique values")
                print(f"   🏥 Diseases: {highlights['diseases_count']} unique values")
                
                return result
            else:
                error_result = {
                    "reasoning": f"Failed to retrieve facets from PRIDE Archive.",
                    "highlights": {
                        "error": f"HTTP {response.status_code}",
                        "url": url,
                        "parameters": params
                    },
                    "error": f"Request failed with status code {response.status_code}",
                    "endpoint_url": url
                }
                return error_result
                
    except Exception as e:
        error_result = {
            "reasoning": f"Error retrieving facets from PRIDE Archive: {str(e)}",
            "highlights": {
                "error": str(e),
                "url": url
            },
            "error": f"Request failed: {str(e)}",
            "endpoint_url": url
        }
        return error_result

@mcp.tool()
async def fetch_projects(
        keyword: str,
        page_size: int = 25,
        page: int = 0,
        sort_direction: str = "DESC",
        sort_fields: str = "downloadCount",
        filters: str = ""
):
    """
    Search for proteomics projects in the PRIDE Archive database.

    Args:
        keyword: The keyword for searching projects (e.g., 'cancer', 'proteomics', 'phosphorylation').
        page_size: The number of results per page (default: 25).
        page: The page number for pagination (default: 0).
        sort_direction: The direction for sorting results ('ASC' or 'DESC', default: DESC).
        sort_fields: The fields to sort by (default: 'downloadCount').
        filters: Comma-separated filters using exact values from get_pride_facets (default: empty).

    Returns:
        A list of project accessions if successful, otherwise a dictionary with an error message.
    """
    
    url = "https://www.ebi.ac.uk/pride/ws/archive/v3/search/projects"
    
    # Build parameters
    params = {
        "keyword": keyword,
        "pageSize": page_size,
        "page": page,
        "sortDirection": sort_direction,
        "sortFields": sort_fields
    }
    
    # Add filters if provided
    if filters:
        params["filter"] = filters
    
    try:
        # Get proxy configuration from environment
        proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
        
        # Only use proxy if it's configured
        client_kwargs = {"timeout": 10.0}
        if proxy:
            client_kwargs["proxy"] = proxy
        
        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                # API returns a list of project objects directly
                if isinstance(data, list):
                    project_accessions = [project.get("accession") for project in data if project.get("accession")]
                else:
                    project_accessions = []
                
                # Extract total_records from response headers
                total_records = response.headers.get("total_records", len(project_accessions))
                try:
                    total_records = int(total_records)
                except (ValueError, TypeError):
                    total_records = len(project_accessions)
                
                result = {
                    "reasoning": f"Successfully found {total_records} total projects matching '{keyword}' (showing {len(project_accessions)} on this page).",
                    "highlights": {
                        "total_projects": total_records,
                        "projects_on_page": len(project_accessions),
                        "keyword": keyword,
                        "filters_applied": filters if filters else "None",
                        "page": page,
                        "page_size": page_size
                    },
                    "data": project_accessions,
                    "endpoint_url": url,
                    "parameters": params,
                    "search_criteria": {
                        "keyword": keyword,
                        "filters": filters,
                        "page_size": page_size,
                        "page": page,
                        "sort_direction": sort_direction,
                        "sort_fields": sort_fields
                    }
                }
                
                print(f"🔍 PRIDE Search Results from: {url}")
                print(f"   📊 Found {len(project_accessions)} projects")
                print(f"   🔍 Keyword: {keyword}")
                print(f"   🏷️  Filters: {filters if filters else 'None'}")
                
                return result
            else:
                error_result = {
                    "reasoning": f"Failed to search PRIDE Archive.",
                    "highlights": {
                        "error": f"HTTP {response.status_code}",
                        "keyword": keyword,
                        "filters": filters
                    },
                    "error": f"Request failed with status code {response.status_code}",
                    "endpoint_url": url,
                    "parameters": params
                }
                return error_result
                
    except Exception as e:
        error_result = {
            "reasoning": f"Error searching PRIDE Archive: {str(e)}",
            "highlights": {
                "error": str(e),
                "keyword": keyword
            },
            "error": f"Request failed: {str(e)}",
            "endpoint_url": url,
            "parameters": params
        }
        return error_result

@mcp.tool()
async def get_project_details(project_accession: str):
    """
    Retrieves detailed information about a specific PRIDE project.
    
    Args:
        project_accession: The PRIDE project accession (e.g., 'PXD000001')
        
    Returns:
        Detailed project information including title, description, submission date, 
        publication info, and experimental metadata.
    """
    url = f"https://www.ebi.ac.uk/pride/ws/archive/v3/projects/{project_accession}"
    
    # Get proxy configuration from environment
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
    
    # Only use proxy if it's configured
    client_kwargs = {"timeout": 10.0}
    if proxy:
        client_kwargs["proxy"] = proxy
    
    async with httpx.AsyncClient(**client_kwargs) as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Extract key information for highlights
            highlights = {
                "project_id": project_accession,
                "title": data.get("title", "N/A"),
                "submission_date": data.get("submissionDate", "N/A"),
                "publication_date": data.get("publicationDate", "N/A"),
                "organism": data.get("organism", {}).get("name", "N/A") if data.get("organism") else "N/A",
                "instrument": data.get("instrument", "N/A"),
                "keywords": data.get("keywords", []),
                "publications": len(data.get("publications", [])),
                "files_count": data.get("filesCount", 0)
            }
            
            result = {
                "reasoning": f"Successfully retrieved detailed information for project {project_accession}.",
                "highlights": highlights,
                "data": data,
                "endpoint_url": url
            }
            
            print(f"📋 Project Details for {project_accession} from: {url}")
            print(f"   🏷️  Title: {highlights['title']}")
            print(f"   📅 Submitted: {highlights['submission_date']}")
            print(f"   🧬 Organism: {highlights['organism']}")
            print(f"   🔬 Instrument: {highlights['instrument']}")
            print(f"   📊 Files: {highlights['files_count']} files")
            print(f"   📚 Publications: {highlights['publications']} papers")
            
            return result
        else:
            error_result = {
                "reasoning": f"Failed to retrieve details for project {project_accession}.",
                "highlights": {
                    "project_id": project_accession,
                    "error": f"HTTP {response.status_code}"
                },
                "error": f"Request failed with status code {response.status_code}",
                "endpoint_url": url
            }
            return error_result

@mcp.tool()
async def get_project_files(project_accession: str, file_type: str = None):
    """
    Retrieves file information for a specific PRIDE project.
    
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
    
    # Get proxy configuration from environment
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY')
    
    # Only use proxy if it's configured
    client_kwargs = {"timeout": 10.0}
    if proxy:
        client_kwargs["proxy"] = proxy
    
    async with httpx.AsyncClient(**client_kwargs) as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            # Analyze file types and create highlights
            file_types = {}
            total_size = 0
            for file_info in data:
                file_type = file_info.get("fileType", "Unknown")
                file_types[file_type] = file_types.get(file_type, 0) + 1
                total_size += file_info.get("fileSize", 0)
            
            highlights = {
                "project_id": project_accession,
                "total_files": len(data),
                "file_types": file_types,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "filter_applied": file_type if file_type else "None",
                "sample_files": [f.get("fileName", "Unknown") for f in data[:3]]
            }
            
            result = {
                "reasoning": f"Successfully retrieved file information for project {project_accession}.",
                "highlights": highlights,
                "data": data,
                "endpoint_url": url,
                "parameters": params
            }
            
            print(f"📁 Project Files for {project_accession} from: {url}")
            print(f"   📊 Total files: {highlights['total_files']}")
            print(f"   📦 File types: {list(highlights['file_types'].keys())}")
            print(f"   💾 Total size: {highlights['total_size_mb']} MB")
            
            return result
        else:
            error_result = {
                "reasoning": f"Failed to retrieve files for project {project_accession}.",
                "highlights": {
                    "project_id": project_accession,
                    "error": f"HTTP {response.status_code}"
                },
                "error": f"Request failed with status code {response.status_code}",
                "endpoint_url": url,
                "parameters": params
            }
            return error_result


# Create the streamable HTTP app for FastAPI integration
def streamable_http_app():
    """Create a streamable HTTP app for FastAPI integration."""
    return mcp.streamable_http_app()

