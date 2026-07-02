"""
FRIDAY - Screen Sharing Assistant
Screen Capture Module

This file handles taking screenshots of your screen.
We'll use the 'mss' library, which is fast and works across platforms.

What is a screenshot?
- A screenshot is a digital image of whatever is displayed on your screen
- It captures pixels (the tiny dots that make up images) from your monitor
- We can save these as image files or send them over the internet

What is mss?
- mss stands for "Multiple Screen Shots"
- It's a Python library that makes capturing screenshots easy
- It's faster than alternatives and works on Windows, Mac, and Linux
"""

# Import the mss library for screen capture
import mss
# Import time to add delays if needed
import time

def take_screenshot():
    """
    This function captures a single screenshot of your primary monitor.
    
    How it works:
    1. Create an mss instance (this is like opening the screen capture tool)
    2. Use the instance to capture the screen
    3. Save or return the image data
    
    Returns:
        image_data: The raw pixel data of the screenshot
    """
    
    # Create an mss instance - this is our screen capture tool
    # Think of it like opening a camera app
    with mss.mss() as sct:
        """
        The 'with' statement is a Python context manager.
        It automatically closes resources when done (like closing the camera).
        This is good practice to prevent memory leaks.
        """
        
        # Capture the primary monitor (monitor 1)
        # monitor=1 means the main screen (you have monitor 1, 2, 3, etc. if you have multiple)
        monitor = sct.monitors[1]
        
        print(f"Capturing screen: {monitor}")
        print(f"Screen size: {monitor['width']}x{monitor['height']} pixels")
        
        # Actually take the screenshot
        # This captures the pixels from the specified monitor
        screenshot = sct.grab(monitor)
        
        print("Screenshot captured successfully!")
        
        # Return the screenshot object
        # This object contains the pixel data and metadata
        return screenshot

def save_screenshot(screenshot, filename="screenshot.png"):
    """
    This function saves a screenshot to a file.
    
    Parameters:
        screenshot: The screenshot object returned by take_screenshot()
        filename: The name of the file to save (default: "screenshot.png")
    
    What is PNG?
        - PNG is an image file format (like JPEG or GIF)
        - It's lossless (no quality loss when saving)
        - Good for screenshots with text and sharp edges
    """
    
    # Import mss's built-in image tools
    from mss.tools import to_png
    
    # Convert the screenshot to PNG format and save to file
    # to_png() converts the raw pixel data to a PNG file
    to_png(screenshot.rgb, screenshot.size, output=filename)
    
    print(f"Screenshot saved to: {filename}")

# This code runs only if you execute this file directly
if __name__ == '__main__':
    """
    This is a test block. When you run 'python screen_capture.py',
    it will take a screenshot and save it so you can see it works.
    """
    print("Testing screen capture...")
    print("Taking a screenshot in 3 seconds...")
    time.sleep(3)  # Wait 3 seconds so you can switch to a different window if you want
    
    # Take the screenshot
    screenshot = take_screenshot()
    
    # Save it to a file
    save_screenshot(screenshot, "test_screenshot.png")
    
    print("Done! Check 'test_screenshot.png' in this folder.")
