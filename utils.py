# utils.py
import os

def check_directory(directory):
    """Проверка существования директории."""
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Директория {directory} не существует.")
    return True