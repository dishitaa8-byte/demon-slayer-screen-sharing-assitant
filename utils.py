"""
FRIDAY - Screen Sharing Assistant
Utility Functions Module

This file contains helper functions used across the application.
These functions handle common tasks like logging, timestamps, and cleanup.

What are utility functions?
- Utility functions are reusable helper functions
- They perform common tasks that multiple parts of the app need
- They keep the main code clean and DRY (Don't Repeat Yourself)
"""

# Import os for file operations
import os
# Import glob for finding files by pattern
import glob
# Import datetime for timestamps
from datetime import datetime
# Import tempfile for temp file management
import tempfile


def cleanup_temp_files():
    """
    Clean up old temporary files from the system temp directory.
    
    This function:
    1. Finds all temporary PNG files created by FRIDAY
    2. Deletes files older than 1 hour
    3. Prevents accumulation of unused screenshots
    
    This should be called periodically or on application exit.
    
    Returns:
        int: Number of files cleaned up
    """
    try:
        # Get the system temp directory
        temp_dir = tempfile.gettempdir()
        
        # Find all PNG files in temp directory
        # Pattern: *.png
        pattern = os.path.join(temp_dir, '*.png')
        temp_files = glob.glob(pattern)
        
        # Get current time
        now = datetime.now()
        cleaned_count = 0
        
        for temp_file in temp_files:
            try:
                # Get file modification time
                file_mtime = datetime.fromtimestamp(os.path.getmtime(temp_file))
                
                # Calculate age in hours
                age_hours = (now - file_mtime).total_seconds() / 3600
                
                # Delete if older than 1 hour
                if age_hours > 1:
                    os.remove(temp_file)
                    cleaned_count += 1
                    
            except Exception:
                # Skip files that can't be deleted
                continue
        
        return cleaned_count
        
    except Exception as e:
        print(f"Warning: Temp file cleanup failed: {e}")
        return 0


def save_logs(log_message, log_file='friday_logs.txt'):
    """
    Save a log message to a log file.
    
    This function:
    1. Appends a timestamped message to the log file
    2. Creates the log file if it doesn't exist
    3. Useful for debugging and tracking usage
    
    Parameters:
        log_message (str): The message to log
        log_file (str): Path to the log file (default: friday_logs.txt)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create timestamp
        timestamp = timestamp()
        
        # Format log entry
        log_entry = f"[{timestamp}] {log_message}\n"
        
        # Append to log file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return True
        
    except Exception as e:
        print(f"Warning: Failed to save log: {e}")
        return False


def timestamp():
    """
    Get a formatted timestamp string.
    
    Returns:
        str: Current time in format: YYYY-MM-DD HH:MM:SS
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def create_log_directory(log_dir='logs'):
    """
    Create a directory for storing logs if it doesn't exist.
    
    Parameters:
        log_dir (str): Path to the log directory (default: logs)
        
    Returns:
        str: Path to the log directory
    """
    try:
        # Create directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        return log_dir
        
    except Exception as e:
        print(f"Warning: Failed to create log directory: {e}")
        return None


def get_file_size(file_path):
    """
    Get the size of a file in human-readable format.
    
    Parameters:
        file_path (str): Path to the file
        
    Returns:
        str: File size in human-readable format (e.g., "1.5 MB")
    """
    try:
        # Get size in bytes
        size_bytes = os.path.getsize(file_path)
        
        # Convert to human-readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.2f} TB"
        
    except Exception as e:
        return "Unknown"
