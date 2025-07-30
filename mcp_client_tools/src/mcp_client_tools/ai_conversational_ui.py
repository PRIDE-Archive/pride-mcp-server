"""
AI-Powered Conversational Web UI for MCP Client Tools.
This provides a chat interface where users can ask natural language questions
and an LLM intelligently uses the MCP tools to answer them.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

from .client import MCPClient
from .tools import PRIDE_EBI_TOOLS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="MCP AI Conversational UI", version="0.1.0")

# Global client instance
mcp_client: Optional[MCPClient] = None

# AI Service with actual LLM integration
class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("CLAUDE_API_KEY")
        self.provider = "gemini" if os.getenv("GEMINI_API_KEY") else "openai" if os.getenv("OPENAI_API_KEY") else "claude"
        self.demo_mode = not bool(self.api_key)
        
        # Initialize LLM client if API key is available
        if not self.demo_mode:
            if self.provider == "gemini":
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    # Use the correct model name for Gemini API v1beta
                    self.model = genai.GenerativeModel('gemini-1.5-pro')
                    logger.info("✅ Gemini AI initialized with gemini-1.5-pro")
                except ImportError:
                    logger.warning("❌ google-generativeai not installed, falling back to demo mode")
                    self.demo_mode = True
            elif self.provider == "openai":
                try:
                    import openai
                    self.client = openai.OpenAI(api_key=self.api_key)
                    logger.info("✅ OpenAI initialized")
                except ImportError:
                    logger.warning("❌ openai not installed, falling back to demo mode")
                    self.demo_mode = True
            else:
                logger.warning(f"❌ Provider {self.provider} not implemented, falling back to demo mode")
                self.demo_mode = True
        else:
            logger.warning("⚠️ No API key found, using demo mode with basic responses")
        
    def analyze_question(self, user_question: str, available_tools: List[Dict]) -> Dict[str, Any]:
        """Use AI to analyze user question and determine which tools to call."""
        
        if self.demo_mode:
            raise ValueError("No API key provided. Please set GEMINI_API_KEY, OPENAI_API_KEY, or CLAUDE_API_KEY environment variable.")
        
        # Use actual LLM for intelligent analysis
        prompt = f"""
You are an AI assistant that helps users search PRIDE Archive proteomics data.
The user asked: "{user_question}"

Available tools:
{json.dumps(available_tools, indent=2)}

Your task is to:
1. Understand what the user wants
2. Decide which tool(s) to call
3. Extract the right parameters

IMPORTANT RULES:
- ALWAYS call get_pride_facets FIRST to determine available filters for any search
- Use the keyword from the user's question to search facets: get_pride_facets(keyword="user_keyword")
- After getting facets, call fetch_projects with appropriate filters based on the facet results
- For questions like "Find X studies", "Show me Y projects", "Search for Z": 
  1. Call get_pride_facets(keyword="X") to find matching filters
  2. Call fetch_projects(keyword="X", filters="matching_filters_from_facets")
  3. Call get_project_details(project_accession="project_accession") to get the project details for top 3 projects to generate synopsis
- For questions like "What organisms are available?", "What filters can I use?": call get_pride_facets only
- When searching for specific organisms (mouse, human, etc.), use the organism name in both facet and project searches
- The facets will help identify the exact filter values to use for more precise searches

CRITICAL: For metadata questions about what's available, ONLY call get_pride_facets:
- "What organisms are available?" → ONLY get_pride_facets
- "What organisms are available in pride archive?" → ONLY get_pride_facets  
- "What filters can I use?" → ONLY get_pride_facets
- "What diseases are available?" → ONLY get_pride_facets
- "What instruments are available?" → ONLY get_pride_facets
- "What software tools are commonly used?" → ONLY get_pride_facets
- "What software tools are commonly used in PRIDE studies?" → ONLY get_pride_facets
- "Show me what's available" → ONLY get_pride_facets
- "List available data" → ONLY get_pride_facets
- "What can I search for?" → ONLY get_pride_facets

DO NOT call fetch_projects for metadata questions about available data.

SPECIAL QUERY HANDLING:
- For "top downloaded", "most popular", "highest downloads", "top 10 downloaded", etc.:
  1. Call get_pride_facets(keyword="") to get all available filters
  2. Call fetch_projects(keyword="", filters="", sort_fields="downloadCount", sort_direction="DESC")
- For "top 10 downloaded project 2024", "most downloaded 2024", etc. (with year):
  1. Call get_pride_facets(keyword="") to get all available filters including submissionDate
  2. Call fetch_projects(keyword="", filters="submissionDate:2024", sort_fields="downloadCount", sort_direction="DESC")
- For "2024 projects", "projects from 2024", etc.:
  1. Call get_pride_facets(keyword="") to get all available filters
  2. Call fetch_projects(keyword="", filters="submissionDate:2024")
- For specific topics (cancer, mouse, human, MaxQuant, etc.), use those as keywords
- For "MaxQuant projects", use keyword="MaxQuant"

IMPORTANT: You must respond with ONLY a valid JSON object, no other text.

Respond with a JSON object like this:
{{
    "intent": "what the user wants to do",
    "tools_to_call": [
        {{
            "tool_name": "tool name",
            "parameters": {{"param": "value"}},
            "reasoning": "why this tool is needed"
        }}
    ],
    "response_template": "how to respond to the user"
}}

Examples:
- "Find human breast cancer studies" → 
  1. get_pride_facets(keyword="human breast cancer") to find matching filters
  2. fetch_projects(keyword="human breast cancer", filters="matching_filters")
  3. get_project_details(project_accession="project_accession") to get the project details for top 3 projects to generate synopsis
- "Show me mouse cancer studies" → 
  1. get_pride_facets(keyword="mouse") to find matching filters
  2. fetch_projects(keyword="cancer", filters="matching_filters")
  3. get_project_details(project_accession="project_accession") to get the project details for top 3 projects to generate synopsis
- "What organisms are available?" → ONLY get_pride_facets (no fetch_projects)
- "What organisms are available in pride archive?" → ONLY get_pride_facets (no fetch_projects)
- "What filters can I use?" → ONLY get_pride_facets (no fetch_projects)
- "What software tools are commonly used in PRIDE studies?" → ONLY get_pride_facets (no fetch_projects)
- "Show me recent proteomics studies" → 
  1. get_pride_facets(keyword="proteomics") to find matching filters
  2. fetch_projects(keyword="proteomics", filters="matching_filters")
  3. get_project_details(project_accession="project_accession") to get the project details for top 3 projects to generate synopsis
- "top 10 downloaded project" → 
  1. get_pride_facets(keyword="") to get all available filters
  2. fetch_projects(keyword="", filters="", sort_fields="downloadCount", sort_direction="DESC")
- "top 10 downloaded project 2024" → 
  1. get_pride_facets(keyword="") to get all available filters
  2. fetch_projects(keyword="", filters="submissionDate:2024", sort_fields="downloadCount", sort_direction="DESC")
- "2024 projects" → 
  1. get_pride_facets(keyword="") to get all available filters
  2. fetch_projects(keyword="", filters="submissionDate:2024")
- "MaxQuant 2024" → 
  1. get_pride_facets(keyword="MaxQuant") to find matching filters
  2. fetch_projects(keyword="MaxQuant", filters="matching_filters") 
  3. get_project_details(project_accession="project_accession") to get the project details for top 3 projects to generate synopsis

Analyze the question and respond with ONLY the JSON object (no markdown, no explanations):
"""
        
        if self.provider == "gemini":
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            result_text = response.choices[0].message.content.strip()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        # Log the raw response for debugging
        logger.info(f"Raw AI response: {result_text}")
        
        # Handle empty or invalid responses
        if not result_text or result_text.strip() == "":
            logger.error("AI returned empty response")
            raise ValueError("AI returned empty response")
        
        # Try to extract JSON from the response (in case AI added extra text)
        try:
            # First try direct JSON parsing
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON from AI response: {result_text}")
                    raise ValueError(f"AI returned invalid JSON: {result_text}")
            else:
                logger.error(f"No JSON found in AI response: {result_text}")
                raise ValueError(f"AI response contains no valid JSON: {result_text}")
        
        logger.info(f"AI Analysis: {result}")
        logger.info(f"🔍 AI determined tools to call: {[tool['tool_name'] for tool in result.get('tools_to_call', [])]}")
        return result
    
    def analyze_facets_for_filters(self, facets_data: Dict, user_keyword: str) -> str:
        """Analyze facets data to determine appropriate filters for project search."""
        
        if not facets_data:
            return ""
        
        # Extract relevant filters based on the user's keyword
        filters = []
        
        # Check for year-related keywords first (priority)
        if any(year in user_keyword.lower() for year in ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013"]):
            # Extract the year from the keyword
            import re
            year_match = re.search(r'20\d{2}', user_keyword)
            if year_match:
                year = year_match.group()
                # Check if this year exists in submissionDate facets
                if "submissionDate" in facets_data and year in facets_data["submissionDate"]:
                    filters.append(f"submissionDate:{year}")
                    logger.info(f"🔍 Added submissionDate filter: {year}")
        
        # Check organisms
        if "organisms" in facets_data:
            organisms = facets_data["organisms"]
            for org_name, count in organisms.items():
                if user_keyword.lower() in org_name.lower() or org_name.lower() in user_keyword.lower():
                    filters.append(f"organism:{org_name}")
        
        # Check diseases
        if "diseases" in facets_data:
            diseases = facets_data["diseases"]
            for disease_name, count in diseases.items():
                if user_keyword.lower() in disease_name.lower() or disease_name.lower() in user_keyword.lower():
                    filters.append(f"disease:{disease_name}")
        
        # Check experiment types
        if "experimentTypes" in facets_data:
            exp_types = facets_data["experimentTypes"]
            for exp_type, count in exp_types.items():
                if user_keyword.lower() in exp_type.lower() or exp_type.lower() in user_keyword.lower():
                    filters.append(f"experimentType:{exp_type}")
        
        # Check keywords
        if "keywords" in facets_data:
            keywords = facets_data["keywords"]
            for keyword, count in keywords.items():
                if user_keyword.lower() in keyword.lower() or keyword.lower() in user_keyword.lower():
                    filters.append(f"keyword:{keyword}")
        
        # Return comma-separated filters
        return ",".join(filters[:5])  # Limit to 5 filters to avoid overly complex queries
    
     
    def generate_response(self, user_question: str, tool_results: List[Dict], intent: str) -> str:
        """Generate a natural language response based on tool results."""
        
        if not tool_results:
            return "I couldn't understand your question. Please try asking about proteomics data, organisms, diseases, or experimental techniques."
        
        if self.demo_mode:
            raise ValueError("No API key provided. Please set GEMINI_API_KEY, OPENAI_API_KEY, or CLAUDE_API_KEY environment variable.")
        
        # Extract project details and create EBI links
        project_details = []
        logger.info(f"🔍 Processing {len(tool_results)} tool results for AI response")
        for result in tool_results:
            logger.info(f"🔍 Processing result: {result.get('tool_name')}")
            logger.info(f"🔍 Result structure: {json.dumps(result, indent=2)}")
            
            if result.get("tool_name") == "get_project_details":
                # Handle the nested MCP response structure
                mcp_result = result.get("result", {})
                if isinstance(mcp_result, dict):
                    # Try different possible data locations
                    data = None
                    if mcp_result.get("data"):
                        data = mcp_result["data"]
                    elif mcp_result.get("result", {}).get("data"):
                        data = mcp_result["result"]["data"]
                    elif mcp_result.get("content") and len(mcp_result["content"]) > 0:
                        # Parse the content field which contains the JSON string
                        try:
                            content_text = mcp_result["content"][0].get("text", "")
                            if content_text:
                                parsed_content = json.loads(content_text)
                                data = parsed_content.get("data")
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.error(f"❌ Error parsing content: {e}")
                    
                    if data and isinstance(data, dict):
                        accession = data.get("accession", "")
                        if accession:
                            ebi_link = f"https://www.ebi.ac.uk/pride/archive/projects/{accession}"
                            project_details.append({
                                "accession": accession,
                                "title": data.get("title", "No title"),
                                "ebi_link": ebi_link,
                                "data": data
                            })
                            logger.info(f"📋 Added project details for {accession}: {data.get('title', 'No title')}")
                        else:
                            logger.warning(f"⚠️ No accession found in data: {data}")
                    else:
                        logger.warning(f"⚠️ No valid data found in result: {mcp_result}")
        
        logger.info(f"📊 Total project details extracted: {len(project_details)}")
        
        # Use actual LLM for intelligent response generation
        prompt = f"""
You are an AI assistant that helps users understand PRIDE Archive proteomics data.

User Question: "{user_question}"
Intent: {intent}

Tool Results:
{json.dumps(tool_results, indent=2)}

Your task is to generate a professional, research-oriented response that:

1. **Header Section**: Start with a clear, descriptive header using markdown H2 (##)
2. **Summary**: Provide a concise summary of search results using professional language
   - IMPORTANT: Use the "total_projects" value from fetch_projects highlights for the total count, NOT the page size
   - If the search found 18 total projects, say "The search identified 18 projects", not "25 projects"
3. **Detailed Projects**: For the top 3 projects with details, create a structured format:
   - Use markdown H3 (###) for each project
   - ALWAYS include clickable EBI links: [PXD######](https://www.ebi.ac.uk/pride/archive/projects/PXD######)
   - List key information in bullet points: Organism, Technique, Keywords, etc.
   - SKIP Project Description field - it's too long and verbose
   - Skip any field that shows "Not available" or "(Title not available)"
   - CRITICAL: Every project accession MUST have a clickable EBI link
4. **Other Project Accessions**: If there are more than 3 projects, include a section called 'Other Project Accessions' and list ONLY the accessions not in the top 3, as clickable EBI links. If there are no other accessions, omit this section.
5. **Professional Tone**: Use academic/research language throughout

CRITICAL FORMATTING REQUIREMENTS:

**Response Structure:**
```markdown
## [Descriptive Header]

[Professional summary of results]

### [PXD000001](https://www.ebi.ac.uk/pride/archive/projects/PXD000001)
- **Title:** [Project title]
- **Organism:** [Organism name]
- **Technique:** [Experimental technique]
- **Keywords:** [Relevant keywords]
- **[Other relevant fields - but NOT Project Description]**

### [PXD000002](https://www.ebi.ac.uk/pride/archive/projects/PXD000002)
[Same format as above]

### [PXD000003](https://www.ebi.ac.uk/pride/archive/projects/PXD000003)
[Same format as above]

## Other Project Accessions
[PXD000004](https://www.ebi.ac.uk/pride/archive/projects/PXD000004), [PXD000005](https://www.ebi.ac.uk/pride/archive/projects/PXD000005)
```

**IMPORTANT:** The 'Other Project Accessions' section must include ONLY the accessions not in the top 3. If there are no others, do not show this section.

**Language Guidelines:**
- Use "Search identified X projects" or "Query returned X projects" or "Database contains X projects"
- NEVER use "I found X projects" or "Showing top 3 of X" or "Found X projects"
- Use professional, academic language
- Keep descriptions concise and informative
- Focus on research-relevant information

**Data Handling:**
- Skip any field that shows "Not available" or "(Title not available)"
- SKIP Project Description field - it's too long and verbose
- Only include meaningful, available information
- CRITICAL: Look for "all_accessions" in the fetch_projects result and include ONLY the accessions not in the top 3 in the 'Other Project Accessions' section
- Create proper EBI links for every accession
- **MOST IMPORTANT**: Use ONLY the actual project details from get_project_details calls. Do NOT make up or generate random titles or information.
- **CRITICAL**: For each project in the top 3, use the exact title, organism, and other details from the get_project_details result. If a field is missing or shows "Not available", skip it entirely.
- **ABSOLUTELY CRITICAL**: You MUST look at the tool_results data and extract the REAL project information from the get_project_details calls. DO NOT generate or invent any information.
- **VERIFICATION**: Before writing any project information, verify that it comes from the actual tool_results data.
- **TOTAL COUNT**: Use "total_projects" from fetch_projects highlights for the correct total count, NOT the page size
- **YEAR FILTERING**: For year-specific queries, verify the returned projects match the requested year. If using submissionDate:2024 filter, the projects should be from 2024. DO NOT state that year filtering is not supported - it IS supported via submissionDate and publicationDate filters.

**FINAL INSTRUCTION**: 
Look at the tool_results data above. Find the get_project_details results and use ONLY the real data from those results. 
If you see "To be added" or "(Title not available)" in the real data, then use that exact text. 
DO NOT include Project Description field - it's too verbose and long.
DO NOT invent or generate any information that is not in the tool_results.
DO NOT make statements about API limitations or unsupported features - the API supports all the features mentioned in the tool results.

Generate a professional, well-structured response:
"""
        
        logger.info(f"🤖 Calling LLM provider: {self.provider}")
        logger.info(f"📝 Prompt length: {len(prompt)} characters")
        
        try:
            if self.provider == "gemini":
                logger.info("🚀 Calling Gemini API...")
                response = self.model.generate_content(prompt)
                logger.info("✅ Gemini API call completed")
                result_text = response.text.strip()
                logger.info(f"📄 Gemini response length: {len(result_text)} characters")
            elif self.provider == "openai":
                logger.info("🚀 Calling OpenAI API...")
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                logger.info("✅ OpenAI API call completed")
                result_text = response.choices[0].message.content.strip()
                logger.info(f"📄 OpenAI response length: {len(result_text)} characters")
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"❌ LLM API call failed: {e}")
            logger.error(f"❌ Provider: {self.provider}")
            logger.error(f"❌ Prompt preview: {prompt[:200]}...")
            raise
        
        # Handle empty responses
        if not result_text or result_text.strip() == "":
            logger.error("AI returned empty response for generate_response")
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
        
        logger.info(f"AI Response: {result_text}")
        return result_text

# Initialize AI service
ai_service = AIService()

# HTML template for the conversational interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PRIDE Archive AI Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="icon" type="image/png" href="https://www.ebi.ac.uk/pride/archive/logo/PRIDE_logo_Archive.png">
                                    <style>
                                    :root {
                                        --primary: #2563EB;
                                        --primary-dark: #1E40AF;
                                        --primary-light: #3B82F6;
                                        --secondary: #6B7280;
                                        --success: #059669;
                                        --warning: #D97706;
                                        --error: #DC2626;
                                        --background: #FFFFFF;
                                        --surface: #F9FAFB;
                                        --surface-light: #F3F4F6;
                                        --border: #E5E7EB;
                                        --border-light: #F3F4F6;
                                        --text-primary: #111827;
                                        --text-secondary: #6B7280;
                                        --text-muted: #9CA3AF;
                                        --accent-blue: #1E40AF;
                                        --accent-indigo: #4F46E5;
                                        --accent-purple: #7C3AED;
                                    }
                                    
                                    body { 
                                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                                        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 50%, #F1F5F9 100%);
                                        min-height: 100vh;
                                        color: var(--text-primary);
                                        line-height: 1.6;
                                    }
        
        .chat-container { height: calc(100vh - 280px); }
        .message { max-width: 85%; }
        
        .user-message { 
            background: var(--primary);
            color: white;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
        }
        
        .assistant-message { 
            background: white;
            color: var(--text-primary);
            border: 1px solid var(--border);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .tool-call { 
            background: #FEF3C7;
            border-left: 4px solid #F59E0B;
            box-shadow: 0 1px 3px rgba(245, 158, 11, 0.1);
        }
        
        .ai-thinking { 
            background: #E0F2FE;
            border-left: 4px solid #0284C7;
            box-shadow: 0 1px 3px rgba(2, 132, 199, 0.1);
        }
        
        .typing-indicator { display: none; }
        
        .glass-effect {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .hover-scale {
            transition: transform 0.2s ease-in-out;
        }
        
        .hover-scale:hover {
            transform: scale(1.02);
        }
        
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-connected { background-color: #059669; }
        .status-disconnected { background-color: #DC2626; }
        .status-connecting { background-color: #F59E0B; }
        
        /* Professional UI styles */
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border);
        }
        
        .button-primary {
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .button-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-1px);
        }
        
        /* Markdown content styles */
        .markdown-content {
            line-height: 1.6;
            color: var(--text-primary);
        }
        
        .markdown-content h1, .markdown-content h2, .markdown-content h3, 
        .markdown-content h4, .markdown-content h5, .markdown-content h6 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .markdown-content h1 { font-size: 1.5em; }
        .markdown-content h2 { font-size: 1.3em; }
        .markdown-content h3 { font-size: 1.1em; }
        
        .markdown-content p {
            margin-bottom: 1em;
        }
        
        .markdown-content ul, .markdown-content ol {
            margin-bottom: 1em;
            padding-left: 1.5em;
        }
        
        .markdown-content li {
            margin-bottom: 0.5em;
        }
        
        .markdown-content strong {
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .markdown-content em {
            font-style: italic;
        }
        
        .markdown-content a {
            color: var(--primary);
            text-decoration: underline;
            transition: color 0.2s;
        }
        
        .markdown-content a:hover {
            color: var(--primary-dark);
        }
        
        .markdown-content code {
            background-color: var(--surface);
            padding: 0.2em 0.4em;
            border-radius: 0.25em;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: var(--text-primary);
        }
        
        .markdown-content pre {
            background-color: var(--pride-light);
            padding: 1em;
            border-radius: 0.5em;
            overflow-x: auto;
            margin-bottom: 1em;
            border-left: 4px solid var(--pride-primary);
        }
        
        .markdown-content blockquote {
            border-left: 4px solid var(--pride-primary);
            padding-left: 1em;
            margin-left: 0;
            color: var(--pride-dark);
            background-color: rgba(112, 189, 189, 0.05);
            padding: 1em;
            border-radius: 0 8px 8px 0;
        }
    </style>
</head>
<body class="min-h-screen">
    <div class="container mx-auto px-4 py-8">
                        <div class="max-w-6xl mx-auto bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 my-8" style="box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.1);">
                            <!-- Header -->
                <div class="relative mb-12">
                    <!-- Background Pattern -->
                    <div class="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-indigo-50 rounded-2xl"></div>
                    
                    <div class="relative px-8 py-12 text-center">
                        <!-- Icon -->
                        <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mb-8 shadow-lg">
                            <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                            </svg>
                        </div>
                        
                        <!-- Title -->
                        <h1 class="text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 bg-clip-text text-transparent mb-4">
                            PRIDE Archive AI Assistant
                        </h1>
                        
                        <!-- Subtitle -->
                        <p class="text-xl text-gray-600 mb-6 max-w-3xl mx-auto leading-relaxed">
                            Your intelligent research companion for exploring proteomics data. Ask natural language questions and get comprehensive insights with automatic project details.
                        </p>
                        
                        <!-- Badge -->
                        <div class="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-md">
                            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            Powered by Gemini AI
                        </div>
                    </div>
                </div>
                
                                                <!-- Status Cards -->
                                <div class="flex justify-center space-x-6 mb-8">
                                    <div class="p-5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-sm border border-blue-100">
                                        <div class="flex items-center">
                                            <span class="status-indicator status-connecting" id="server-status-indicator"></span>
                                            <div class="ml-3">
                                                <p class="text-sm font-semibold text-gray-900">Server Status</p>
                                                <p class="text-xs text-gray-600" id="server-status">Connecting...</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="p-5 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-sm border border-green-100">
                                        <div class="flex items-center">
                                            <span class="status-indicator status-connected" id="ai-status-indicator"></span>
                                            <div class="ml-3">
                                                <p class="text-sm font-semibold text-gray-900">AI Assistant</p>
                                                <p class="text-xs text-gray-600" id="ai-status">Ready</p>
                                                <p class="text-xs text-green-600 font-medium">Gemini Powered</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
            </div>

                                               <!-- Chat Interface -->
                                   <div class="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/30 overflow-hidden">
                                       <!-- Chat Header -->
                                       <div class="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                                <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                            </div>
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900">AI Assistant</h3>
                                <p class="text-sm text-gray-600">Ready to help with your research</p>
                            </div>
                        </div>
                        <div class="text-gray-500 text-sm">
                            <span id="message-count">0</span> messages
                        </div>
                    </div>
                </div>

                <!-- Chat Messages -->
                <div id="chat-messages" class="chat-container overflow-y-auto p-6 space-y-4 bg-white">
                    <div class="assistant-message message p-4 rounded-lg bg-gray-50 border border-gray-200">
                        <div class="flex items-start space-x-3">
                            <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                                AI
                            </div>
                            <div class="flex-1">
                                <h3 class="font-semibold text-gray-900 mb-3">Welcome to PRIDE Archive AI Assistant! 👋</h3>
                                <p class="text-gray-700 mb-4">I'm your intelligent research companion for exploring proteomics data. Here's what I can do:</p>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                                    <div class="flex items-center space-x-2">
                                        <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                                        <span class="text-sm text-gray-600">Understand natural language questions</span>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                                        <span class="text-sm text-gray-600">Intelligently select research tools</span>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
                                        <span class="text-sm text-gray-600">Extract optimal search parameters</span>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <span class="w-2 h-2 bg-orange-500 rounded-full"></span>
                                        <span class="text-sm text-gray-600">Auto-generate project synopses</span>
                                    </div>
                                </div>
                                <p class="text-sm text-gray-500">Try asking about organisms, diseases, experimental techniques, or specific research topics!</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Typing Indicator -->
                <div id="typing-indicator" class="typing-indicator p-4 border-t border-gray-200 bg-gray-50 hidden">
                    <div class="flex items-center space-x-3">
                        <div class="flex space-x-1">
                            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                        </div>
                        <span class="text-gray-600 font-medium">AI is analyzing your question...</span>
                    </div>
                </div>

                <!-- Input Area -->
                <div class="border-t border-gray-200 p-4 bg-white">
                    <form id="chat-form" class="flex space-x-3">
                        <div class="flex-1 relative">
                            <input type="text" id="message-input" 
                                   class="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                                   placeholder="Ask about proteomics research, organisms, diseases, or experimental techniques...">
                            <div class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                                </svg>
                            </div>
                        </div>
                        <button type="submit" 
                                class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 font-medium">
                            <span class="flex items-center space-x-2">
                                <span>Send</span>
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                                </svg>
                            </span>
                        </button>
                    </form>
                </div>
            </div>

            <!-- Example Questions -->
            <div class="mt-8 p-8 bg-gradient-to-br from-blue-50 via-white to-indigo-50 rounded-xl shadow-lg border border-blue-100">
                <div class="flex items-center space-x-3 mb-6">
                    <div class="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center">
                        <span class="text-blue-600 text-lg">💡</span>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900">Quick Start Examples</h3>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    <button onclick="askQuestion('What organisms are available in PRIDE Archive?')" 
                            class="hover-scale text-left p-4 bg-white/80 backdrop-blur-sm border border-white/30 rounded-lg hover:bg-white hover:shadow-md transition-all duration-200 group">
                        <div class="flex items-center space-x-3">
                            <span class="text-2xl">🧬</span>
                            <div>
                                <p class="font-medium text-gray-900 group-hover:text-blue-600">Available Organisms</p>
                                <p class="text-xs text-gray-600">Explore species diversity</p>
                            </div>
                        </div>
                    </button>
                    <button onclick="askQuestion('Find human breast cancer proteomics studies')" 
                            class="hover-scale text-left p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-all duration-200 group">
                        <div class="flex items-center space-x-3">
                            <span class="text-2xl">🔬</span>
                            <div>
                                <p class="font-medium text-gray-900 group-hover:text-blue-600">Cancer Research</p>
                                <p class="text-xs text-gray-600">Human breast cancer studies</p>
                            </div>
                        </div>
                    </button>
                    <button onclick="askQuestion('Show me mouse proteomics experiments on cancer')" 
                            class="hover-scale text-left p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-all duration-200 group">
                        <div class="flex items-center space-x-3">
                            <span class="text-2xl">🐭</span>
                            <div>
                                <p class="font-medium text-gray-900 group-hover:text-blue-600">Mouse Studies</p>
                                <p class="text-xs text-gray-600">Proteomics experiments</p>
                            </div>
                        </div>
                    </button>
                    <button onclick="askQuestion('Search for Alzheimer disease datasets')" 
                            class="hover-scale text-left p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-all duration-200 group">
                        <div class="flex items-center space-x-3">
                            <span class="text-2xl">🧠</span>
                            <div>
                                <p class="font-medium text-gray-900 group-hover:text-blue-600">Neurological</p>
                                <p class="text-xs text-gray-600">Alzheimer's research</p>
                            </div>
                        </div>
                    </button>
                    <button onclick="askQuestion('Find studies from 2024 using MaxQuant software')" 
                            class="hover-scale text-left p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-all duration-200 group">
                        <div class="flex items-center space-x-3">
                            <span class="text-2xl">📅</span>
                            <div>
                                <p class="font-medium text-gray-900 group-hover:text-blue-600">Recent Studies</p>
                                <p class="text-xs text-gray-600">2024 + MaxQuant</p>
                            </div>
                        </div>
                    </button>
                    <button onclick="askQuestion('What software tools are commonly used in PRIDE studies?')" 
                            class="hover-scale text-left p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-all duration-200 group">
                        <div class="flex items-center space-x-3">
                            <span class="text-2xl">🛠️</span>
                            <div>
                                <p class="font-medium text-gray-900 group-hover:text-blue-600">Software Tools</p>
                                <p class="text-xs text-gray-600">Popular analysis tools</p>
                            </div>
                        </div>
                    </button>
                </div>
            </div>

            <!-- Help Section -->
            <div class="mt-8 p-8 bg-gradient-to-br from-indigo-50 via-white to-purple-50 rounded-xl shadow-lg border border-indigo-100">
                <div class="flex items-center justify-between mb-6">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center">
                            <span class="text-blue-600 text-lg">❓</span>
                        </div>
                        <h3 class="text-xl font-bold text-gray-900">MCP Server Integration Help</h3>
                    </div>
                    <button onclick="toggleHelp()" id="help-toggle" class="text-gray-600 hover:text-blue-600 transition-colors">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l-7-7 7-7"></path>
                        </svg>
                    </button>
                </div>
                
                <div id="help-content" class="space-y-6">
                    <!-- Server Information -->
                    <div class="bg-white/80 backdrop-blur-sm border border-white/30 rounded-lg p-4">
                        <h4 class="font-semibold text-gray-900 mb-3">📋 Server Information</h4>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                            <div>
                                <span class="font-medium text-blue-600">URL:</span>
                                <span class="text-gray-700">http://localhost:9000</span>
                            </div>
                            <div>
                                <span class="font-medium text-blue-600">Name:</span>
                                <span class="text-gray-700">PRIDE Archive MCP Server</span>
                            </div>
                            <div>
                                <span class="font-medium text-blue-600">Description:</span>
                                <span class="text-gray-700">Access proteomics data from PRIDE Archive</span>
                            </div>
                        </div>
                    </div>

                    <!-- Available Tools -->
                    <div class="bg-white/80 backdrop-blur-sm border border-white/30 rounded-lg p-4">
                        <h4 class="font-semibold text-gray-900 mb-3">🛠️ Available Tools</h4>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                            <div class="flex items-center space-x-2">
                                <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                                <span class="text-gray-700"><strong>get_pride_facets:</strong> Get available filters and facets</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span class="w-2 h-2 bg-green-500 rounded-full"></span>
                                <span class="text-gray-700"><strong>fetch_projects:</strong> Search for proteomics projects</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
                                <span class="text-gray-700"><strong>get_project_details:</strong> Get detailed project information</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span class="w-2 h-2 bg-orange-500 rounded-full"></span>
                                <span class="text-gray-700"><strong>get_project_files:</strong> Get project file information</span>
                            </div>
                        </div>
                    </div>

                    <!-- Integration Guides -->
                    <div class="bg-white/80 backdrop-blur-sm border border-white/30 rounded-lg p-4">
                        <h4 class="font-semibold text-gray-900 mb-3">📖 Integration Guides</h4>
                        <p class="text-sm text-gray-700 mb-3">Click on any integration below to see detailed step-by-step instructions:</p>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            <button onclick="showIntegrationHelp('claude')" class="text-left p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 cursor-pointer group">
                                <div class="flex items-center space-x-2">
                                    <span class="text-lg">🤖</span>
                                    <div>
                                        <p class="font-medium text-gray-900 group-hover:text-blue-600">Claude Desktop</p>
                                        <p class="text-xs text-gray-600">Settings → Extensions</p>
                                    </div>
                                </div>
                            </button>
                            <button onclick="showIntegrationHelp('cursor')" class="text-left p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 cursor-pointer group">
                                <div class="flex items-center space-x-2">
                                    <span class="text-lg">💻</span>
                                    <div>
                                        <p class="font-medium text-gray-900 group-hover:text-blue-600">Cursor IDE</p>
                                        <p class="text-xs text-gray-600">Settings → MCP</p>
                                    </div>
                                </div>
                            </button>
                            <button onclick="showIntegrationHelp('chatgpt')" class="text-left p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 cursor-pointer group">
                                <div class="flex items-center space-x-2">
                                    <span class="text-lg">💬</span>
                                    <div>
                                        <p class="font-medium text-gray-900 group-hover:text-blue-600">ChatGPT</p>
                                        <p class="text-xs text-gray-600">With MCP Plugin</p>
                                    </div>
                                </div>
                            </button>
                        </div>
                    </div>


                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        let ws = null;
        const chatMessages = document.getElementById('chat-messages');
        const messageInput = document.getElementById('message-input');
        const chatForm = document.getElementById('chat-form');
        const typingIndicator = document.getElementById('typing-indicator');
        
        // Configure marked for security
        marked.setOptions({
            breaks: true,
            gfm: true,
            sanitize: false
        });

        // Initialize WebSocket connection
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = protocol + '//' + window.location.host + '/ws';
            
            console.log('Attempting to connect to WebSocket:', wsUrl);
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected successfully!');
                document.getElementById('server-status').textContent = 'Connected';
                document.getElementById('server-status-indicator').className = 'status-indicator status-connected';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                document.getElementById('server-status').textContent = 'Disconnected';
                document.getElementById('server-status-indicator').className = 'status-indicator status-disconnected';
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                document.getElementById('server-status').textContent = 'Error';
                document.getElementById('server-status-indicator').className = 'status-indicator status-disconnected';
            };
        }

        let currentProgressStep = null;
        
        function handleMessage(data) {
            hideTypingIndicator();
            
            if (data.type === 'ai_analysis') {
                // Show AI analysis progress
                if (!currentProgressStep) {
                    currentProgressStep = showProgressStep('AI Analysis', 'Analyzing your question and determining required tools...');
                } else {
                    updateProgressStep(currentProgressStep, 'AI Analysis', 'Analyzing your question and determining required tools...');
                }
                addAIAnalysisMessage(data);
            } else if (data.type === 'assistant') {
                addAssistantMessage(data.content);
                // Remove progress step when complete
                if (currentProgressStep) {
                    currentProgressStep.remove();
                    currentProgressStep = null;
                }
            } else if (data.type === 'tool_call') {
                // Update progress based on tool being called
                const toolName = data.tool;
                let stepName = 'Processing';
                let stepMessage = 'Executing tools...';
                
                if (toolName === 'get_pride_facets') {
                    stepName = 'Fetching Filters';
                    stepMessage = 'Retrieving available filters from PRIDE Archive...';
                } else if (toolName === 'fetch_projects') {
                    stepName = 'Searching Projects';
                    stepMessage = 'Searching for projects in PRIDE Archive...';
                } else if (toolName === 'get_project_details') {
                    stepName = 'Getting Project Details';
                    stepMessage = `Retrieving detailed information for project ${data.parameters?.project_accession || '...'}...`;
                }
                
                if (!currentProgressStep) {
                    currentProgressStep = showProgressStep(stepName, stepMessage);
                } else {
                    updateProgressStep(currentProgressStep, stepName, stepMessage);
                }
                
                addToolCallMessage(data);
            } else if (data.type === 'error') {
                addErrorMessage(data.error);
                // Remove progress step on error
                if (currentProgressStep) {
                    currentProgressStep.remove();
                    currentProgressStep = null;
                }
            } else if (data.type === 'progress') {
                // Handle custom progress messages
                if (!currentProgressStep) {
                    currentProgressStep = showProgressStep(data.step || 'Processing', data.message || 'Working...');
                } else {
                    updateProgressStep(currentProgressStep, data.step || 'Processing', data.message || 'Working...', data.complete);
                }
            }
        }

        function addUserMessage(content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'user-message message p-6 rounded-2xl ml-auto';
            messageDiv.innerHTML = `
                <div class="flex items-start space-x-3">
                    <div class="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                        You
                    </div>
                    <div class="flex-1">
                        <p class="text-white">${escapeHtml(content)}</p>
                    </div>
                </div>
            `;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            updateMessageCount();
        }

        function addAssistantMessage(content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'assistant-message message p-6 rounded-2xl';
            
            // Parse markdown content to HTML
            const parsedContent = marked.parse(content);
            
            messageDiv.innerHTML = `
                <div class="flex items-start space-x-3">
                    <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                        AI
                    </div>
                    <div class="flex-1">
                        <div class="prose prose-sm max-w-none markdown-content">${parsedContent}</div>
                    </div>
                </div>
            `;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            updateMessageCount();
        }

        function updateMessageCount() {
            const messageCount = document.querySelectorAll('.message').length;
            document.getElementById('message-count').textContent = messageCount;
        }



        function addAIAnalysisMessage(data) {
            // AI analysis messages are hidden for cleaner UI
            return;
        }

        function addToolCallMessage(data) {
            // Tool call messages are hidden for cleaner UI
            return;
        }

        function addErrorMessage(error) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'bg-gradient-to-r from-red-50 to-red-100 border border-red-200 text-red-800 px-6 py-4 rounded-2xl relative message';
            messageDiv.innerHTML = `
                <div class="flex items-start space-x-3">
                    <div class="w-8 h-8 bg-gradient-to-r from-red-400 to-red-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                        ⚠️
                    </div>
                    <div class="flex-1">
                        <p class="font-semibold text-red-800 mb-1">Error</p>
                        <p class="text-red-700">${escapeHtml(error)}</p>
                    </div>
                </div>
            `;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            updateMessageCount();
        }

        function showTypingIndicator() {
            typingIndicator.style.display = 'block';
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function hideTypingIndicator() {
            typingIndicator.style.display = 'none';
        }

        function showProgressStep(step, message) {
            const progressDiv = document.createElement('div');
            progressDiv.className = 'progress-step message p-4 rounded-xl';
            progressDiv.innerHTML = `
                <div class="flex items-start space-x-3">
                    <div class="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                        ⚡
                    </div>
                    <div class="flex-1">
                        <div class="flex items-center space-x-2 mb-2">
                            <span class="font-semibold text-blue-800">${step}</span>
                            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                        </div>
                        <p class="text-sm text-gray-600">${message}</p>
                    </div>
                </div>
            `;
            chatMessages.appendChild(progressDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            updateMessageCount();
            return progressDiv;
        }

        function updateProgressStep(progressDiv, step, message, isComplete = false) {
            if (progressDiv) {
                const icon = progressDiv.querySelector('.w-8.h-8');
                const stepText = progressDiv.querySelector('.font-semibold');
                const messageText = progressDiv.querySelector('.text-sm');
                const spinner = progressDiv.querySelector('.animate-spin');
                
                if (isComplete) {
                    icon.innerHTML = '✅';
                    icon.className = 'w-8 h-8 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center text-white text-sm font-semibold';
                    if (spinner) spinner.style.display = 'none';
                } else {
                    icon.innerHTML = '⚡';
                    icon.className = 'w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-semibold';
                    if (spinner) spinner.style.display = 'block';
                }
                
                stepText.textContent = step;
                messageText.textContent = message;
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function askQuestion(question) {
            messageInput.value = question;
            chatForm.dispatchEvent(new Event('submit'));
        }

        // Help functions
        function toggleHelp() {
            const helpContent = document.getElementById('help-content');
            const helpToggle = document.getElementById('help-toggle');
            const isHidden = helpContent.classList.contains('hidden');
            
            if (isHidden) {
                helpContent.classList.remove('hidden');
                helpToggle.innerHTML = `
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
                    </svg>
                `;
            } else {
                helpContent.classList.add('hidden');
                helpToggle.innerHTML = `
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                `;
            }
        }

        function showIntegrationHelp(tool) {
            const helpSteps = {
                claude: [
                    "1. Open Claude Desktop",
                    "2. Go to Settings → Extensions", 
                    "3. Click 'Add Extension'",
                    "4. Select 'MCP (Model Context Protocol)'",
                    "5. Enter Server URL: http://localhost:9000",
                    "6. Enter Server Name: PRIDE Archive MCP Server",
                    "7. Click 'Add' and restart if prompted"
                ],
                cursor: [
                    "1. Open Cursor IDE",
                    "2. Go to Settings (Cmd/Ctrl + ,)",
                    "3. Search for 'MCP' or 'Model Context Protocol'",
                    "4. Add new MCP server configuration:",
                    "   - Server URL: http://localhost:9000",
                    "   - Server Name: PRIDE Archive MCP Server",
                    "5. Save and restart Cursor if needed"
                ],
                chatgpt: [
                    "1. Install the MCP plugin for ChatGPT",
                    "2. Open ChatGPT and go to Settings",
                    "3. Navigate to Plugins section",
                    "4. Add new MCP server:",
                    "   - Server URL: http://localhost:9000",
                    "   - Server Name: PRIDE Archive MCP Server",
                    "5. Save and restart ChatGPT"
                ]
            };

            const steps = helpSteps[tool] || [];
            const toolNames = {
                claude: "Claude Desktop",
                cursor: "Cursor IDE", 
                chatgpt: "ChatGPT"
            };

            var message = "## " + toolNames[tool] + " Integration\\n\\n";
            message += steps.join("\\n");
            
            // Add as assistant message
            addAssistantMessage(message);
        }

        // Event listeners
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (!message) return;

            addUserMessage(message);
            messageInput.value = '';
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                showTypingIndicator();
                ws.send(JSON.stringify({
                    type: 'user_message',
                    content: message
                }));
            } else {
                addErrorMessage('WebSocket not connected. Please refresh the page.');
            }
        });

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            connectWebSocket();
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the AI conversational web interface."""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    global mcp_client
    return {
        "status": "healthy" if mcp_client else "no_client",
        "server_url": mcp_client.mcp_server_url if mcp_client else None,
        "ai_provider": ai_service.provider,
        "ai_available": not ai_service.demo_mode,
        "message": "Set GEMINI_API_KEY, OPENAI_API_KEY, or CLAUDE_API_KEY environment variable to enable AI"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "user_message":
                await handle_user_message(websocket, message_data["content"])
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))

async def handle_user_message(websocket: WebSocket, user_message: str):
    """Handle user message using AI to intelligently call MCP tools."""
    global mcp_client
    
    if not mcp_client:
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": "MCP client not initialized"
        }))
        return
    
    try:
        # Step 1: Use AI to analyze the question and determine what tools to call
        await websocket.send_text(json.dumps({
            "type": "progress",
            "step": "AI Analysis",
            "message": "Analyzing your question and determining required tools..."
        }))
        
        try:
            ai_analysis = ai_service.analyze_question(user_message, PRIDE_EBI_TOOLS)
        except Exception as ai_error:
            logger.error(f"AI analysis failed: {ai_error}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "error": f"AI analysis failed: {str(ai_error)}"
            }))
            return
        
        # Show AI analysis to user
        await websocket.send_text(json.dumps({
            "type": "ai_analysis",
            "intent": ai_analysis["intent"],
            "tools_to_call": ai_analysis["tools_to_call"]
        }))
        
        # Step 2: Execute the tools that AI determined are needed
        tool_results = []
        project_accessions = []
        facets_data = None
        enhanced_search_performed = False
        
        for tool_call in ai_analysis["tools_to_call"]:
            tool_name = tool_call["tool_name"]
            parameters = tool_call["parameters"]
            logger.info(f"🔧 Executing tool: {tool_name} with parameters: {parameters}")
            
            # Execute tool
            try:
                # Show tool call
                await websocket.send_text(json.dumps({
                    "type": "tool_call",
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": None
                }))
                
                result = await mcp_client.call_tool_async(tool_name, parameters)
                tool_results.append({
                    "tool_name": tool_name,
                    "result": result
                })
                
                # Show result
                await websocket.send_text(json.dumps({
                    "type": "tool_call",
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": result
                }))
                
                # If this was a get_pride_facets call, automatically call fetch_projects afterward
                if tool_name == "get_pride_facets" and result.get("data"):
                    facets_data = result["data"]
                    logger.info(f"📊 Retrieved facets data with {len(facets_data)} categories")
                    
                    await websocket.send_text(json.dumps({
                        "type": "progress",
                        "step": "Analyzing Filters",
                        "message": f"Analyzing {len(facets_data)} available filters to refine search..."
                    }))
                    
                    # Extract the original keyword from the user's question
                    user_keyword = user_message.lower()
                    
                    # Analyze facets to find relevant filters
                    filters = ai_service.analyze_facets_for_filters(facets_data, user_keyword)
                    
                    logger.info(f"🔍 Calling fetch_projects with keyword: {user_keyword}, filters: {filters}")
                    
                    await websocket.send_text(json.dumps({
                        "type": "progress",
                        "step": "Searching Projects",
                        "message": "Searching for projects in PRIDE Archive..."
                    }))
                    
                    # Always call fetch_projects after facets
                    try:
                        # Show tool call for fetch_projects
                        await websocket.send_text(json.dumps({
                            "type": "tool_call",
                            "tool": "fetch_projects",
                            "parameters": {
                                "keyword": user_keyword,
                                "filters": filters,
                                "page_size": 25
                            },
                            "result": None
                        }))
                        
                        # Call fetch_projects
                        projects_result = await mcp_client.call_tool_async("fetch_projects", {
                            "keyword": user_keyword,
                            "filters": filters,
                            "page_size": 25
                        })
                        
                        tool_results.append({
                            "tool_name": "fetch_projects",
                            "result": projects_result
                        })
                        
                        # Show result
                        await websocket.send_text(json.dumps({
                            "type": "tool_call",
                            "tool": "fetch_projects",
                            "parameters": {
                                "keyword": user_keyword,
                                "filters": filters,
                                "page_size": 25
                            },
                            "result": projects_result
                        }))
                        
                        logger.info(f"✅ fetch_projects completed")
                        
                    except Exception as e:
                        logger.error(f"❌ Error calling fetch_projects: {e}")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "error": f"Failed to call fetch_projects: {str(e)}"
                        }))
                

                
                # If this was a fetch_projects call, extract project accessions for details
                if tool_name == "fetch_projects":
                    logger.info(f"🔍 Processing fetch_projects result structure: {json.dumps(result, indent=2)}")
                    
                    # Extract project accessions from the result - handle nested MCP structure
                    projects_data = None
                    if result.get("data"):
                        projects_data = result["data"]
                    elif result.get("result", {}).get("content"):
                        try:
                            content_text = result["result"]["content"][0].get("text", "")
                            if content_text:
                                parsed_content = json.loads(content_text)
                                projects_data = parsed_content.get("data")
                                logger.info(f"🔍 Extracted projects_data from nested structure: {projects_data}")
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.error(f"❌ Error parsing fetch_projects content: {e}")
                    
                    if projects_data and isinstance(projects_data, list) and len(projects_data) > 0:
                        # Store all project accessions for the AI response
                        all_project_accessions = []
                        for project in projects_data:
                            if isinstance(project, str):
                                # If the data is already a list of accessions
                                all_project_accessions.append(project)
                        
                        # Get top 3 project accessions for detailed retrieval
                        project_accessions = all_project_accessions[:3]
                        
                        logger.info(f"🔍 Found {len(all_project_accessions)} total projects, getting details for top 3: {project_accessions}")
                        
                        # Store all accessions in the result for AI to use
                        result["all_accessions"] = all_project_accessions
                        
                        # Also store in tool_results for AI to access
                        for tool_result in tool_results:
                            if tool_result["tool_name"] == "fetch_projects":
                                tool_result["result"]["all_accessions"] = all_project_accessions
                                break
                        
                        # Log additional info about the search results
                        if result.get("highlights"):
                            highlights = result["highlights"]
                            logger.info(f"📊 Search summary: {highlights.get('total_projects', 0)} total projects found for keyword '{highlights.get('keyword', 'unknown')}'")
                    else:
                        logger.info(f"🔍 No valid project data found in fetch_projects result: {projects_data}")
                else:
                    logger.info(f"🔍 Tool {tool_name} result: {result.get('data', 'No data')}")
                
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": f"Failed to call {tool_name}: {str(e)}"
                }))
        
        # Step 2.5: Automatically get details for top 3 projects if we have search results
        logger.info(f"🔍 Checking for project accessions: {project_accessions}")
        logger.info(f"🔍 Total tool results so far: {len(tool_results)}")
        logger.info(f"🔍 Type of project_accessions: {type(project_accessions)}")
        if project_accessions and len(project_accessions) > 0:
            logger.info(f"📋 Getting details for {len(project_accessions)} projects: {project_accessions}")
            
            await websocket.send_text(json.dumps({
                "type": "progress",
                "step": "Getting Project Details",
                "message": f"Retrieving detailed information for {len(project_accessions)} projects..."
            }))
            
            successful_details = 0
            for i, accession in enumerate(project_accessions, 1):
                try:
                    logger.info(f"📋 Getting details for project {i}/{len(project_accessions)}: {accession}")
                    
                    # Show tool call for project details
                    await websocket.send_text(json.dumps({
                        "type": "tool_call",
                        "tool": "get_project_details",
                        "parameters": {"project_accession": accession},
                        "result": None
                    }))
                    
                    # Get project details
                    logger.info(f"🔍 Calling get_project_details with accession: '{accession}' (type: {type(accession)})")
                    details_result = await mcp_client.call_tool_async("get_project_details", {"project_accession": accession})
                    
                    # Extract title for logging - handle the nested MCP response structure
                    title = "No title"
                    project_data = None
                    
                    # Try to extract data from the nested MCP response
                    if details_result.get("result", {}).get("content"):
                        try:
                            content_text = details_result["result"]["content"][0].get("text", "")
                            if content_text:
                                parsed_content = json.loads(content_text)
                                project_data = parsed_content.get("data")
                                if project_data and isinstance(project_data, dict):
                                    title = project_data.get("title", "No title")
                                    logger.info(f"📋 Project {accession} details: {json.dumps(project_data, indent=2)}")
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.error(f"❌ Error parsing project details for {accession}: {e}")
                    
                    logger.info(f"✅ Got details for project {accession}: {title}")
                    successful_details += 1
                    
                    # Add to tool results with the correct structure
                    tool_results.append({
                        "tool_name": "get_project_details",
                        "result": details_result
                    })
                    
                    # Show result
                    await websocket.send_text(json.dumps({
                        "type": "tool_call",
                        "tool": "get_project_details",
                        "parameters": {"project_accession": accession},
                        "result": details_result
                    }))
                    
                except Exception as e:
                    logger.error(f"❌ Error getting details for project {accession}: {e}")
            
            logger.info(f"📊 Project details summary: {successful_details}/{len(project_accessions)} projects successfully retrieved")
        else:
            logger.info("🔍 No project accessions found, skipping automatic project details retrieval")
        
        # Step 3: Generate natural language response using AI
        await websocket.send_text(json.dumps({
            "type": "progress",
            "step": "Generating Response",
            "message": "Creating a comprehensive response with project details..."
        }))
        
        # Debug: Log what tool results are being passed to AI
        logger.info(f"🔍 DEBUG: Tool results being passed to AI:")
        for i, result in enumerate(tool_results):
            logger.info(f"  {i+1}. {result.get('tool_name')}: {result.get('result', 'No result')}")
        
        try:
            response = ai_service.generate_response(user_message, tool_results, ai_analysis["intent"])
        except Exception as response_error:
            logger.error(f"Response generation failed: {response_error}")
            response = f"I apologize, but I encountered an error while generating a response: {str(response_error)}"
        
        await websocket.send_text(json.dumps({
            "type": "assistant",
            "content": response
        }))
        
    except Exception as e:
        logger.error(f"Error handling user message: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))

def create_ai_conversational_ui(mcp_server_url: str, port: int = 9090):
    """Create and configure the AI conversational web UI."""
    global mcp_client
    
    # Initialize MCP client
    mcp_client = MCPClient(mcp_server_url)
    logger.info(f"Initialized MCP client for server: {mcp_server_url}")
    
    return app

def run_ai_conversational_ui(mcp_server_url: str, port: int = 9090, host: str = "127.0.0.1"):
    """Run the AI conversational web UI."""
    app = create_ai_conversational_ui(mcp_server_url, port)
    
    logger.info(f"Starting AI conversational UI on http://{host}:{port}")
    logger.info(f"Log Level: INFO")
    uvicorn.run(app, host=host, port=port, log_level="info", access_log=True)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP AI Conversational UI")
    parser.add_argument("--server-url", default="http://127.0.0.1:9000", 
                       help="MCP server URL")
    parser.add_argument("--port", type=int, default=9090, 
                       help="Web server port")
    parser.add_argument("--host", default="127.0.0.1", 
                       help="Web server host")
    
    args = parser.parse_args()
    
    run_ai_conversational_ui(args.server_url, args.port, args.host) 