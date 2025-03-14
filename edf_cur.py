# edf_cur.py
import os
from mne.io import read_raw_edf
from tqdm import tqdm

def is_edf_corrupted(file_path):
    """Checks if an EDF file is corrupted using MNE."""
    try:
        raw = read_raw_edf(file_path, preload=False, verbose=False)  # Use only read_raw_edf
        return False
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return True

def find_and_delete_corrupted_edf(directory):
    """Searches for and deletes corrupted EDF files in the specified directory."""
    deleted_files = 0
    edf_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".edf"):
                edf_files.append(os.path.join(root, file))

    for file_path in tqdm(edf_files, desc="Checking files", unit="file"):
        if is_edf_corrupted(file_path):
            print(f"File is corrupted: {file_path}")
            try:
                os.remove(file_path)
                print(f"File deleted: {file_path}")
                deleted_files += 1
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    print(f"Deleted corrupted files: {deleted_files}")

if __name__ == "__main__":
    directory = input("Enter the directory path: ").strip()

    if os.path.isdir(directory):
        find_and_delete_corrupted_edf(directory)
    else:
        print("The specified directory does not exist.")