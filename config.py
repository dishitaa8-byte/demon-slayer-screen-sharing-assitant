"""
FRIDAY - Screen Sharing Assistant
Configuration Module

This file loads and manages environment variables from the .env file.
It provides a centralized place for all configuration settings.

What is python-dotenv?
- python-dotenv is a library that reads variables from a .env file
- It loads them into environment variables that Python can access
- This keeps sensitive data (API keys) out of your source code
- It follows the 12-factor app methodology for configuration management

Why separate config from code?
- Security: API keys aren't hardcoded in source files
- Flexibility: Different configs for development/production
- Portability: Easy to change settings without editing code
"""

# Import dotenv to load environment variables from .env file
from dotenv import load_dotenv
# Import os to access environment variables
import os

# Load environment variables from .env file
# This reads the .env file and makes the variables available via os.environ
load_dotenv()

class Config:
    """
    Configuration class that holds all application settings.
    
    Using a class makes it easy to:
    - Access config in a structured way (Config.API_KEY instead of os.getenv())
    - Add validation logic in the future
    - Provide type hints for better IDE support
    """
    
    # NVIDIA API Configuration
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    
    # NVIDIA API Base URL (OpenAI-compatible endpoint)
    NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1"
    NVIDIA_BASE_URL = NVIDIA_API_URL  # Alias for backward compatibility
    
    # Chat model for text conversations
    # Using meta/llama-3.3-70b-instruct as a good default
    CHAT_MODEL = "meta/llama-3.2-11b-vision-instruct"
    MODEL_NAME = CHAT_MODEL  # Alias for backward compatibility
    
    # Vision model for screen analysis
    # Meta Llama 3.2 11B Vision - tested and working with NVIDIA API
    VISION_MODEL = "meta/llama-3.2-11b-vision-instruct"
    
    @classmethod
    def validate(cls):
        """
        Validate that required configuration is present.
        
        This method checks if critical settings are missing.
        Call this at application startup to fail fast if config is invalid.
        
        Raises:
            ValueError: If required configuration is missing
        """
        if not cls.NVIDIA_API_KEY:
            raise ValueError(
                "NVIDIA_API_KEY not found in environment variables. "
                "Please add it to your .env file."
            )
        
        return True

# Validate configuration on module load
# This ensures we catch missing API keys early
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please check your .env file and ensure NVIDIA_API_KEY is set.")
