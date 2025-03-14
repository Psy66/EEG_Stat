# edf_dubl_seek.py
import hashlib
import os
from collections import defaultdict

from tqdm import tqdm

def calculate_file_hash(file_path, hash_algorithm="md5", chunk_size=8192):
    """Calculates the file hash for content verification."""
    hash_func = hashlib.new(hash_algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def find_duplicate_files(directory):
    """Searches for duplicate files in the specified directory."""
    size_dict = defaultdict(list)

    # Collect files by size
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            size_dict[file_size].append(file_path)

    hash_dict = defaultdict(list)

    # Check hash for files with the same size
    for size, paths in tqdm(size_dict.items(), desc="Checking files", unit="group"):
        if len(paths) > 1:
            for path in paths:
                file_hash = calculate_file_hash(path)
                hash_dict[file_hash].append(path)

    # Filter duplicates
    duplicates = {hash_val: paths for hash_val, paths in hash_dict.items() if len(paths) > 1}

    return duplicates

def delete_duplicates(duplicates):
    """Deletes all duplicates except one."""
    for hash_val, paths in duplicates.items():
        for path in tqdm(paths[1:], desc="Deleting duplicates", unit="file"):
            try:
                os.remove(path)
                print(f"Deleted file: {path}")
            except OSError as e:
                print(f"Error deleting file {path}: {e}")

def main():
    """Main function for finding and deleting duplicates."""
    directory = input("Enter the directory path: ")
    duplicates = find_duplicate_files(directory)

    if duplicates:
        print("Found duplicate files (matching content):")
        for hash_val, paths in duplicates.items():
            print(f"Hash: {hash_val}")
            for path in paths:
                print(f"  {path}")

        delete_duplicates(duplicates)
    else:
        print("No duplicate files found.")

if __name__ == "__main__":
    main()