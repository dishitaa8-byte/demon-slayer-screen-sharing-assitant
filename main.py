"""
FRIDAY - Screen Sharing Assistant
Main Entry Point

This file is the main entry point for the FRIDAY assistant.
It runs an interactive command-line interface for chatting with the AI.

What is a CLI (Command Line Interface)?
- A CLI is a text-based interface for interacting with programs
- Users type commands and the program responds with text
- It's simpler than a GUI (Graphical User Interface) but very powerful

Current Mode:
- This version runs in interactive chat mode
- Future versions will add:
  - Web server mode (Flask)
  - Vision/screen analysis
  - Voice input/output
  - Memory system
  - Tool calling
  - Overlay UI
"""

# Import the Friday LLM instance
from llm import friday
# Import vision module for screen capture
from vision import vision
# Import sys for clean exit
import sys

def print_welcome():
    """
    Print a welcome message when the program starts.
    """
    print("=" * 60)
    print("FRIDAY - AI Desktop Assistant")
    print("Inspired by Iron Man's FRIDAY")
    print("=" * 60)
    print("Type your message and press Enter to chat.")
    print("Type '/analyze' to analyze your screen.")
    print("Type '/region' to analyze a specific screen region.")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("=" * 60)
    print()

def handle_analyze_command():
    """
    Handle the /analyze command for screen analysis.
    
    This function:
    1. Captures the full screen
    2. Encodes the image to base64
    3. Prompts the user for a question
    4. Sends the image and question to the vision model
    5. Prints FRIDAY's analysis
    """
    try:
        print("Capturing screen...")
        
        # Capture the screen
        image_path = vision.capture_screen()
        
        # Encode to base64
        image_base64 = vision.encode_image_base64(image_path)
        
        # Get user's question
        print("\nWhat would you like to know about your screen?")
        user_question = input("Question: ")
        
        if not user_question.strip():
            print("No question provided. Skipping analysis.")
            return
        
        # Analyze the screen
        print("\nFRIDAY is analyzing your screen...")
        analysis = friday.analyze_screen(image_base64, user_question)
        
        # Print the analysis
        print("\nFRIDAY:")
        print(analysis)
        
    except Exception as e:
        print(f"\nError during screen analysis: {e}")
        print("Please try again.")

def handle_region_command():
    """
    Handle the /region command for region-specific screen analysis.
    
    This function:
    1. Prompts the user for region coordinates
    2. Captures the specified region
    3. Encodes the image to base64
    4. Prompts the user for a question
    5. Sends the image and question to the vision model
    6. Prints FRIDAY's analysis
    """
    try:
        print("Enter region coordinates (x1 y1 x2 y2)")
        print("Example: 100 100 800 600")
        coords_input = input("Coordinates: ")
        
        # Parse coordinates
        try:
            x1, y1, x2, y2 = map(int, coords_input.strip().split())
        except ValueError:
            print("Invalid coordinates. Please enter four numbers separated by spaces.")
            return
        
        # Capture the region
        print(f"Capturing region ({x1}, {y1}) to ({x2}, {y2})...")
        image_path = vision.capture_region(x1, y1, x2, y2)
        
        # Encode to base64
        image_base64 = vision.encode_image_base64(image_path)
        
        # Get user's question
        print("\nWhat would you like to know about this region?")
        user_question = input("Question: ")
        
        if not user_question.strip():
            print("No question provided. Skipping analysis.")
            return
        
        # Analyze the region
        print("\nFRIDAY is analyzing the region...")
        analysis = friday.analyze_screen(image_base64, user_question)
        
        # Print the analysis
        print("\nFRIDAY:")
        print(analysis)
        
    except Exception as e:
        print(f"\nError during region analysis: {e}")
        print("Please try again.")

def main():
    """
    Main function that runs the interactive conversation loop.
    
    This function:
    1. Prints a welcome message
    2. Enters an infinite loop to continuously accept user input
    3. Sends each message to the LLM
    4. Prints the AI's response
    5. Handles errors gracefully
    6. Exits when user types 'quit' or 'exit'
    """
    
    # Print welcome message
    print_welcome()
    
    # Main conversation loop
    while True:
        """
        while True creates an infinite loop.
        We'll break out of it when the user wants to quit.
        """
        
        try:
            # Get user input
            # input() waits for the user to type something and press Enter
            user_input = input("You: ")
            
            # Check if user wants to quit
            # strip() removes leading/trailing whitespace
            # lower() converts to lowercase for case-insensitive comparison
            if user_input.strip().lower() in ['quit', 'exit']:
                print("\nGoodbye! FRIDAY signing off.")
                # Clean up temp files before exit
                vision.cleanup_temp_files()
                break  # Exit the loop
            
            # Check for /analyze command
            if user_input.strip() == '/analyze':
                handle_analyze_command()
                continue  # Skip to next iteration
            
            # Check for /region command
            if user_input.strip() == '/region':
                handle_region_command()
                continue  # Skip to next iteration
            
            # Skip empty messages
            if not user_input.strip():
                print("Please enter a message.")
                continue  # Skip to next iteration
            
            # Send message to FRIDAY and get response
            # ask_friday() handles the API call and streaming
            response = friday.ask_friday(user_input)
            
            # Response is already printed by ask_friday() due to streaming
            # No need to print it again here
            
        except ValueError as e:
            """
            Handle ValueError - usually invalid input or empty responses
            """
            print(f"\nError: {e}")
            print("Please try again.")
            
        except ConnectionError as e:
            """
            Handle ConnectionError - network issues
            """
            print(f"\nConnection Error: {e}")
            print("Please check your internet connection and try again.")
            
        except KeyboardInterrupt:
            """
            Handle Ctrl+C - user wants to exit immediately
            """
            print("\n\nInterrupted by user. Goodbye!")
            sys.exit(0)
            
        except Exception as e:
            """
            Handle any other unexpected errors
            """
            print(f"\nUnexpected Error: {e}")
            print("Please try again or contact support if the issue persists.")

# This is the main block that runs when you execute the file
if __name__ == '__main__':
    """
    This code only runs if you run this file directly (python main.py)
    It won't run if you import this file as a module in another file.
    """
    try:
        main()
    except Exception as e:
        """
        Catch any errors that occur during startup
        """
        print(f"Startup Error: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)
