# utils.py
import os

def check_directory(directory):
    """Checks if the directory exists."""
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist.")
    return True