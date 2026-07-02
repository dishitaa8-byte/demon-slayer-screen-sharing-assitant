"""
FRIDAY - Screen Sharing Assistant
Vision Module

This file handles all screen capture and image processing functionality.
It provides functions for capturing screens, regions, and encoding images.

What is screen capture?
- Screen capture is the process of taking a screenshot of your display
- It's used to analyze what's currently visible on your screen
- FRIDAY uses this to provide visual assistance

What is region capture?
- Region capture captures only a specific area of the screen
- This is useful when you want to focus on a particular window or element
- It's more efficient than capturing the entire screen

What is base64 encoding?
- Base64 is a way to represent binary data (images) as text
- It allows images to be sent in JSON requests to APIs
- The format is: data:image/png;base64,<encoded_string>
"""

# Import mss for screen capture
import mss
# Import tempfile for creating temporary files
import tempfile
# Import os for file operations
import os
# Import base64 for encoding images
import base64
# Import PIL for image processing
from PIL import Image


class VisionCapture:
    """
    Vision capture class that handles all screen and image operations.
    
    This class encapsulates:
    - Full screen capture
    - Region capture
    - Image encoding
    - Temporary file management
    """
    
    def __init__(self):
        """
        Initialize the vision capture module.
        
        Sets up temporary file tracking for cleanup.
        """
        # Track temporary files for cleanup
        self.temp_files = []
    
    def capture_screen(self):
        """
        Capture the entire screen.
        
        This function:
        1. Uses mss to capture the primary monitor
        2. Saves the capture to a temporary file
        3. Returns the path to the temporary file
        
        Returns:
            str: Path to the temporary screenshot file
            
        Raises:
            Exception: If screen capture fails
        """
        try:
            # Create a temporary file for the screenshot
            # delete=False allows us to manually manage cleanup
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.png',
                delete=False
            )
            temp_path = temp_file.name
            temp_file.close()
            
            # Create a fresh mss instance for this capture
            # Using context manager ensures proper cleanup
            with mss.mss() as sct:
                # Capture the primary monitor (monitor 1)
                # mss returns a dictionary with image data
                screenshot = sct.shot(output=temp_path)
            
            # Track the temp file for cleanup
            self.temp_files.append(temp_path)
            
            return temp_path
            
        except Exception as e:
            raise Exception(f"Screen capture failed: {e}")
    
    def capture_region(self, x1, y1, x2, y2):
        """
        Capture a specific region of the screen.
        
        This function:
        1. Defines a region using the provided coordinates
        2. Captures only that region
        3. Saves to a temporary file
        4. Returns the path to the temporary file
        
        Parameters:
            x1 (int): Left coordinate of the region
            y1 (int): Top coordinate of the region
            x2 (int): Right coordinate of the region
            y2 (int): Bottom coordinate of the region
            
        Returns:
            str: Path to the temporary screenshot file
            
        Raises:
            ValueError: If coordinates are invalid
            Exception: If region capture fails
        """
        try:
            # Validate coordinates
            if x1 >= x2 or y1 >= y2:
                raise ValueError("Invalid coordinates: x1 must be < x2 and y1 must be < y2")
            
            if x1 < 0 or y1 < 0:
                raise ValueError("Coordinates cannot be negative")
            
            # Define the capture region
            # mss expects: {'top': y1, 'left': x1, 'width': x2-x1, 'height': y2-y1}
            region = {
                'top': y1,
                'left': x1,
                'width': x2 - x1,
                'height': y2 - y1
            }
            
            # Create a temporary file for the screenshot
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.png',
                delete=False
            )
            temp_path = temp_file.name
            temp_file.close()
            
            # Create a fresh mss instance for this capture
            # Using context manager ensures proper cleanup
            with mss.mss() as sct:
                # Capture the specified region
                screenshot = sct.grab(region)
                
                # Convert to PIL Image and save
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                img.save(temp_path)
            
            # Track the temp file for cleanup
            self.temp_files.append(temp_path)
            
            return temp_path
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Region capture failed: {e}")
    
    def encode_image_base64(self, image_path):
        """
        Convert an image file to base64 encoded string.
        
        This function:
        1. Reads the image file
        2. Encodes it to base64
        3. Returns the data URI format
        
        Parameters:
            image_path (str): Path to the image file
            
        Returns:
            str: Base64 encoded image in data URI format
                 Format: data:image/png;base64,<encoded_string>
                 
        Raises:
            FileNotFoundError: If image file doesn't exist
            Exception: If encoding fails
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Read the image file in binary mode
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Encode to base64
            base64_string = base64.b64encode(image_data).decode('utf-8')
            
            # Return in data URI format
            return f"data:image/png;base64,{base64_string}"
            
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            raise Exception(f"Image encoding failed: {e}")
    
    def cleanup_temp_files(self):
        """
        Clean up all temporary files created during this session.
        
        This function:
        1. Iterates through all tracked temp files
        2. Deletes each file
        3. Clears the tracking list
        
        This should be called when the application exits
        to prevent accumulating temporary files.
        """
        try:
            for temp_file in self.temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            # Clear the tracking list
            self.temp_files.clear()
            
        except Exception as e:
            # Log error but don't raise - cleanup shouldn't crash the app
            print(f"Warning: Some temp files could not be cleaned: {e}")


# Create a global instance for easy access
vision = VisionCapture()
