import google.generativeai as genai
from typing import Optional, Dict, Any
import json
from config.settings import settings

class GeminiService:
    """Service class for interacting with Google's Gemini Pro API."""
    
    def __init__(self):
        """Initialize the Gemini service."""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required for Gemini service")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def analyze_proteomics_data(self, data: Dict[str, Any], context: str = "") -> str:
        """
        Analyze proteomics data using Gemini Pro.
        
        Args:
            data: The proteomics data to analyze
            context: Additional context for the analysis
            
        Returns:
            Analysis result as a string
        """
        try:
            # Create a comprehensive prompt for proteomics analysis
            prompt = f"""
            You are an expert bioinformatician specializing in proteomics data analysis.
            
            Context: {context}
            
            Please analyze the following proteomics data and provide insights:
            
            {json.dumps(data, indent=2)}
            
            Please provide:
            1. A summary of the key findings
            2. Biological significance of the data
            3. Potential research implications
            4. Any notable patterns or anomalies
            
            Format your response in a clear, scientific manner suitable for researchers.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error analyzing data with Gemini: {str(e)}"
    
    def enhance_search_results(self, search_results: Dict[str, Any], query: str) -> str:
        """
        Enhance search results with AI-generated insights.
        
        Args:
            search_results: The search results to enhance
            query: The original search query
            
        Returns:
            Enhanced analysis as a string
        """
        try:
            prompt = f"""
            You are analyzing proteomics search results from the PRIDE Archive database.
            
            Original Query: {query}
            
            Search Results:
            {json.dumps(search_results, indent=2)}
            
            Please provide:
            1. A summary of what was found
            2. The significance of these results
            3. Suggestions for next steps in research
            4. Any notable patterns in the data
            
            Keep your response concise and focused on the scientific value of these results.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error enhancing results with Gemini: {str(e)}"
    
    def generate_research_suggestions(self, project_data: Dict[str, Any]) -> str:
        """
        Generate research suggestions based on project data.
        
        Args:
            project_data: The project data to analyze
            
        Returns:
            Research suggestions as a string
        """
        try:
            prompt = f"""
            You are a research advisor analyzing a proteomics project.
            
            Project Data:
            {json.dumps(project_data, indent=2)}
            
            Based on this project data, please suggest:
            1. Potential follow-up experiments
            2. Related research directions
            3. Collaboration opportunities
            4. Data analysis approaches
            
            Focus on actionable research suggestions that could advance the field.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating suggestions with Gemini: {str(e)}"

# Global Gemini service instance
gemini_service: Optional[GeminiService] = None

def get_gemini_service() -> Optional[GeminiService]:
    """Get the global Gemini service instance."""
    global gemini_service
    
    if not settings.ENABLE_GEMINI:
        return None
    
    if gemini_service is None and settings.GEMINI_API_KEY:
        try:
            gemini_service = GeminiService()
        except Exception as e:
            print(f"Failed to initialize Gemini service: {e}")
            return None
    
    return gemini_service 