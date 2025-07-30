import os
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings and configuration."""
    
    def __init__(self):
        """Initialize settings and load configuration."""
        self.config_file = "config/ai_config.json"
        self.load_ai_config()
    
    def load_ai_config(self):
        """Load AI configuration from file."""
        self._load_ai_config_impl()
    
    def reload_ai_config(self):
        """Reload AI configuration from file."""
        self._load_ai_config_impl()
    
    def _load_ai_config_impl(self):
        """Internal implementation of loading AI configuration."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Set AI provider
                self.AI_PROVIDER = config.get("ai_provider", "gemini")
                
                # Set Gemini settings (use environment variable as default)
                gemini_config = config.get("gemini", {})
                self.GEMINI_API_KEY = gemini_config.get("api_key", "") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                self.GEMINI_MODEL = gemini_config.get("model", "gemini-2.0-flash-exp")
                
                # Set Claude settings
                claude_config = config.get("claude", {})
                self.CLAUDE_API_KEY = claude_config.get("api_key", "") or os.getenv("CLAUDE_API_KEY")
                self.CLAUDE_MODEL = claude_config.get("model", "claude-3-5-sonnet-20241022")
                self.CLAUDE_BASE_URL = claude_config.get("base_url", "https://api.anthropic.com")
                
                # Set OpenAI settings
                openai_config = config.get("openai", {})
                self.OPENAI_API_KEY = openai_config.get("api_key", "") or os.getenv("OPENAI_API_KEY")
                self.OPENAI_MODEL = openai_config.get("model", "gpt-4o")
                self.OPENAI_BASE_URL = openai_config.get("base_url", "https://api.openai.com")
                
                # Set Ollama settings
                ollama_config = config.get("ollama", {})
                self.OLLAMA_BASE_URL = ollama_config.get("base_url", "http://localhost:11434")
                self.OLLAMA_MODEL = ollama_config.get("model", "llama3.2")
                
                # Set Custom provider settings
                custom_config = config.get("custom", {})
                self.CUSTOM_API_KEY = custom_config.get("api_key", "") or os.getenv("CUSTOM_API_KEY")
                self.CUSTOM_MODEL = custom_config.get("model", "")
                self.CUSTOM_BASE_URL = custom_config.get("base_url", "")
                self.CUSTOM_PROVIDER_NAME = custom_config.get("provider_name", "Custom Provider")
            else:
                # Default values if config file doesn't exist
                self.AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
                self.GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
                self.CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
                self.CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
                self.CLAUDE_BASE_URL = os.getenv("CLAUDE_BASE_URL", "https://api.anthropic.com")
                self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
                self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
                self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
                self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
                self.CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY")
                self.CUSTOM_MODEL = os.getenv("CUSTOM_MODEL", "")
                self.CUSTOM_BASE_URL = os.getenv("CUSTOM_BASE_URL", "")
                self.CUSTOM_PROVIDER_NAME = os.getenv("CUSTOM_PROVIDER_NAME", "Custom Provider")
        except Exception as e:
            print(f"Error loading AI config: {e}")
            # Fallback to environment variables
            self.AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
            self.GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            self.CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
            self.CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
            self.CLAUDE_BASE_URL = os.getenv("CLAUDE_BASE_URL", "https://api.anthropic.com")
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
            self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
            self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
            self.CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY")
            self.CUSTOM_MODEL = os.getenv("CUSTOM_MODEL", "")
            self.CUSTOM_BASE_URL = os.getenv("CUSTOM_BASE_URL", "")
            self.CUSTOM_PROVIDER_NAME = os.getenv("CUSTOM_PROVIDER_NAME", "Custom Provider")
    
    def save_ai_config(self):
        """Save AI configuration to file."""
        try:
            config = {
                "ai_provider": self.AI_PROVIDER,
                "gemini": {
                    "api_key": self.GEMINI_API_KEY or "",
                    "model": self.GEMINI_MODEL
                },
                "claude": {
                    "api_key": self.CLAUDE_API_KEY or "",
                    "model": self.CLAUDE_MODEL,
                    "base_url": self.CLAUDE_BASE_URL
                },
                "openai": {
                    "api_key": self.OPENAI_API_KEY or "",
                    "model": self.OPENAI_MODEL,
                    "base_url": self.OPENAI_BASE_URL
                },
                "ollama": {
                    "base_url": self.OLLAMA_BASE_URL,
                    "model": self.OLLAMA_MODEL
                },
                "custom": {
                    "api_key": self.CUSTOM_API_KEY or "",
                    "model": self.CUSTOM_MODEL,
                    "base_url": self.CUSTOM_BASE_URL,
                    "provider_name": self.CUSTOM_PROVIDER_NAME
                }
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving AI config: {e}")
    
    # Server Configuration
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "9000"))
    
    # Feature Flags
    ENABLE_AI = os.getenv("ENABLE_AI", "true").lower() == "true"
    
    def validate_ai_config(self) -> Dict[str, Any]:
        """Validate AI provider configuration."""
        config_status = {
            "provider": self.AI_PROVIDER,
            "enabled": self.ENABLE_AI,
            "valid": False,
            "message": "",
            "api_key_configured": False
        }
        
        if not self.ENABLE_AI:
            config_status["message"] = "AI features are disabled"
            return config_status
        
        if self.AI_PROVIDER == "gemini":
            if not self.GEMINI_API_KEY:
                config_status["message"] = "GEMINI_API_KEY not found in environment variables"
                return config_status
            config_status["valid"] = True
            config_status["api_key_configured"] = True
            config_status["message"] = "Gemini Pro integration enabled"
            
        elif self.AI_PROVIDER == "claude":
            if not self.CLAUDE_API_KEY:
                config_status["message"] = "CLAUDE_API_KEY not found in environment variables"
                return config_status
            config_status["valid"] = True
            config_status["api_key_configured"] = True
            config_status["message"] = "Claude integration enabled"
            
        elif self.AI_PROVIDER == "openai":
            if not self.OPENAI_API_KEY:
                config_status["message"] = "OPENAI_API_KEY not found in environment variables"
                return config_status
            config_status["valid"] = True
            config_status["api_key_configured"] = True
            config_status["message"] = "OpenAI integration enabled"
            
        elif self.AI_PROVIDER == "ollama":
            # For Ollama, we don't need an API key, just check if the URL is accessible
            config_status["valid"] = True
            config_status["api_key_configured"] = True
            config_status["message"] = f"Ollama integration enabled (URL: {self.OLLAMA_BASE_URL})"
            
        elif self.AI_PROVIDER == "custom":
            if not self.CUSTOM_API_KEY:
                config_status["message"] = "CUSTOM_API_KEY not found in environment variables"
                return config_status
            config_status["valid"] = True
            config_status["api_key_configured"] = True
            config_status["message"] = f"Custom AI integration enabled ({self.CUSTOM_PROVIDER_NAME})"
            
        else:
            config_status["message"] = f"Unknown AI provider: {self.AI_PROVIDER}"
            
        return config_status
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get current AI configuration."""
        return {
            "provider": self.AI_PROVIDER,
            "gemini": {
                "api_key": self.GEMINI_API_KEY,
                "model": self.GEMINI_MODEL
            },
            "claude": {
                "api_key": self.CLAUDE_API_KEY,
                "model": self.CLAUDE_MODEL,
                "base_url": self.CLAUDE_BASE_URL
            },
            "openai": {
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "base_url": self.OPENAI_BASE_URL
            },
            "ollama": {
                "base_url": self.OLLAMA_BASE_URL,
                "model": self.OLLAMA_MODEL
            },
            "custom": {
                "api_key": self.CUSTOM_API_KEY,
                "model": self.CUSTOM_MODEL,
                "base_url": self.CUSTOM_BASE_URL,
                "provider_name": self.CUSTOM_PROVIDER_NAME
            }
        }

# Global settings instance
settings = Settings()
