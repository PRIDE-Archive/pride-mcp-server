import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings and configuration."""
    
    # Gemini Pro API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # Server Configuration
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "9000"))
    
    # Feature Flags
    ENABLE_GEMINI = os.getenv("ENABLE_GEMINI", "true").lower() == "true"
    
    @classmethod
    def validate_gemini_config(cls):
        """Validate Gemini API configuration."""
        if cls.ENABLE_GEMINI and not cls.GEMINI_API_KEY:
            print("⚠️  Warning: GEMINI_API_KEY not found in environment variables.")
            print("   Set GEMINI_API_KEY in your .env file or environment variables to enable Gemini features.")
            return False
        return True

# Global settings instance
settings = Settings()
