"""
FRIDAY - Screen Sharing Assistant
LLM (Large Language Model) Module

This file handles all communication with NVIDIA's OpenAI-compatible API.
It manages conversation history, sends requests, and streams responses.

What is an LLM?
- LLM stands for Large Language Model
- It's an AI trained on vast amounts of text to understand and generate human-like responses
- Examples include GPT-4, Claude, Llama, etc.
- NVIDIA provides access to various LLMs through their API

What is streaming?
- Streaming means receiving the response piece by piece as it's generated
- Instead of waiting for the complete response, you get chunks in real-time
- This provides a better user experience (like ChatGPT's typing effect)

What is conversation history?
- LLMs are stateless - each request is independent
- To maintain context, we send previous messages along with new ones
- This allows the AI to remember what was said earlier
"""

# Import OpenAI SDK (NVIDIA's API is OpenAI-compatible)
from openai import OpenAI
# Import config for API key and settings
from config import Config
# Import sys for exiting on critical errors
import sys

class FridayLLM:
    """
    FRIDAY's LLM interface class.
    
    This class encapsulates all logic for communicating with the NVIDIA API.
    Using a class makes it easy to:
    - Maintain conversation state
    - Add features (memory, tools, etc.) in the future
    - Test the LLM interface independently
    """
    
    def __init__(self):
        """
        Initialize the LLM client and conversation history.
        
        The OpenAI client is configured to use NVIDIA's base URL
        instead of OpenAI's default URL, but the API is compatible.
        """
        # Initialize OpenAI client with NVIDIA's endpoint
        # This uses the same SDK as OpenAI, but points to NVIDIA's servers
        self.client = OpenAI(
            base_url=Config.NVIDIA_BASE_URL,
            api_key=Config.NVIDIA_API_KEY
        )
        
        # Conversation history - stores all messages in the current session
        # Each message is a dict with 'role' and 'content'
        self.conversation_history = []
        
        # Initialize with system prompt
        self._initialize_system_prompt()
    
    def _initialize_system_prompt(self):
        """
        Add the system prompt to conversation history.
        
        The system prompt sets the AI's personality and behavior.
        It's sent first and guides all subsequent responses.
        """
        system_prompt = """You are Friday, an intelligent AI assistant inspired by Iron Man's FRIDAY.

You are helpful, calm, intelligent, and concise.
You explain things step by step.
You assist users with coding, productivity, desktop tasks, and problem solving.
When analyzing screenshots later, describe what you observe before giving instructions.
Always think carefully before answering."""
        
        # Add system message to history
        self.conversation_history.append({
            "role": "system",
            "content": system_prompt
        })
    
    def ask_friday(self, user_message):
        """
        Send a user message to FRIDAY and get a streaming response.
        
        This function:
        1. Adds the user message to conversation history
        2. Sends the entire history to the LLM
        3. Streams the response token by token
        4. Adds the AI response to conversation history
        5. Returns the complete response
        
        Parameters:
            user_message (str): The user's input message
            
        Returns:
            str: The complete AI response
            
        Raises:
            ValueError: If API key is invalid or response is empty
            ConnectionError: If network request fails
            Exception: For other API errors
        """
        # Validate input
        if not user_message or not user_message.strip():
            raise ValueError("User message cannot be empty")
        
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Create the chat completion request with streaming enabled
            # stream=True makes the response come in chunks
            print("Before API call")
            stream = self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=self.conversation_history,
                stream=True,
                temperature=0.7,  # Controls randomness (0.0 = deterministic, 1.0 = creative)
                max_tokens=2048   # Maximum length of response
            )
            print("API call returned")
            
            # Collect the complete response
            complete_response = ""
            
            # Process the stream chunk by chunk
            print("FRIDAY: ", end="", flush=True)  # Print prefix without newline
            
            for chunk in stream:
                # Each chunk contains a delta (change) with the new content
                if chunk.choices and chunk.choices[0].delta.content:
                    # Extract the content from the chunk
                    content = chunk.choices[0].delta.content
                    # Print it immediately for streaming effect
                    print(content, end="", flush=True)
                    # Add to complete response
                    complete_response += content
            
            print()  # New line after response is complete
            
            # Validate we got a response
            if not complete_response or not complete_response.strip():
                raise ValueError("Received empty response from API")
            
            # Add AI response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": complete_response
            })
            
            return complete_response
            
        except Exception as e:
            # Handle different types of errors
            error_message = str(e)
            
            # Check for authentication errors (invalid API key)
            if "authentication" in error_message.lower() or "unauthorized" in error_message.lower():
                raise ValueError(f"Invalid NVIDIA API key. Please check your .env file. Error: {error_message}")
            
            # Check for rate limit errors
            elif "rate limit" in error_message.lower() or "429" in error_message:
                raise Exception(f"Rate limit exceeded. Please wait and try again. Error: {error_message}")
            
            # Check for network/connection errors
            elif "connection" in error_message.lower() or "network" in error_message.lower():
                raise ConnectionError(f"Network error: {error_message}")
            
            # Generic error
            else:
                raise Exception(f"API Error: {error_message}")
    
    def clear_history(self):
        """
        Clear the conversation history (except system prompt).
        
        Useful for starting a fresh conversation.
        """
        # Keep only the system prompt
        self.conversation_history = [self.conversation_history[0]]
    
    def get_history_length(self):
        """
        Get the number of messages in conversation history (excluding system prompt).
        
        Returns:
            int: Number of user/assistant messages
        """
        return len(self.conversation_history) - 1  # Exclude system prompt
    
    def analyze_screen(self, image_base64, user_question):
        """
        Analyze a screenshot using the vision model.
        
        This function:
        1. Sends the image and question to the vision model
        2. Uses the OpenAI-compatible API with image_url format
        3. Returns the AI's analysis of the screen
        
        Parameters:
            image_base64 (str): Base64 encoded image in data URI format
            user_question (str): The user's question about the screen
            
        Returns:
            str: The AI's analysis of the screen
            
        Raises:
            ValueError: If image is invalid or response is empty
            ConnectionError: If network request fails
            Exception: For other API errors
        """
        # Validate inputs
        if not image_base64 or not image_base64.strip():
            raise ValueError("Image data cannot be empty")
        
        if not user_question or not user_question.strip():
            raise ValueError("User question cannot be empty")
        
        # System prompt for vision analysis
        system_prompt = """You are FRIDAY, an intelligent screen assistant inspired by Iron Man's FRIDAY.

Describe what you observe before giving instructions.

Identify:
- applications
- buttons
- text
- menus
- warnings
- error messages

Explain step by step.

Be concise, helpful, and friendly."""
        
        # Construct the message with image
        # Using OpenAI-compatible format with image_url
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_question
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_base64
                        }
                    }
                ]
            }
        ]
        
        try:
            # Create the chat completion request with vision model
            # Note: Vision requests typically don't use streaming
            response = self.client.chat.completions.create(
                model=Config.VISION_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            
            # Extract the response content
            analysis = response.choices[0].message.content
            
            # Validate we got a response
            if not analysis or not analysis.strip():
                raise ValueError("Received empty response from API")
            
            return analysis
            
        except ValueError as e:
            raise e
        except Exception as e:
            # Handle different types of errors
            error_message = str(e)
            
            # Check for authentication errors (invalid API key)
            if "authentication" in error_message.lower() or "unauthorized" in error_message.lower():
                raise ValueError(f"Invalid NVIDIA API key. Please check your .env file. Error: {error_message}")
            
            # Check for rate limit errors
            elif "rate limit" in error_message.lower() or "429" in error_message:
                raise Exception(f"Rate limit exceeded. Please wait and try again. Error: {error_message}")
            
            # Check for network/connection errors
            elif "connection" in error_message.lower() or "network" in error_message.lower():
                raise ConnectionError(f"Network error: {error_message}")
            
            # Check for invalid image errors
            elif "image" in error_message.lower() or "invalid" in error_message.lower():
                raise ValueError(f"Invalid image format. Error: {error_message}")
            
            # Check for timeout errors
            elif "timeout" in error_message.lower():
                raise Exception(f"Request timeout. Please try again. Error: {error_message}")
            
            # Generic error
            else:
                raise Exception(f"API Error: {error_message}")


# Create a global instance for easy access
# This allows importing and using: from llm import friday; friday.ask_friday("hello")
friday = FridayLLM()
