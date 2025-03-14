# edf_rename.py
import os
from mne.io import read_raw_edf
from tqdm import tqdm

def get_edf_metadata(file_path):
    """Extracts metadata from an EDF file."""
    try:
        raw = read_raw_edf(file_path, preload=False)
        info = raw.info
        subject_info = info.get('subject_info', {})
        first_name = subject_info.get('first_name', '').strip().capitalize()
        middle_name = subject_info.get('middle_name', '').strip().capitalize()
        last_name = subject_info.get('last_name', '').strip().capitalize()
        patient_name = f"{first_name}_{middle_name}_{last_name}".strip()
        if not patient_name:
            patient_name = 'Unknown'
        recording_date = info.get('meas_date', None)
        if recording_date:
            recording_date = recording_date.strftime('%Y-%m-%d_%H-%M-%S')
        else:
            recording_date = 'Unknown_Date'
        return patient_name, recording_date
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None, None

def format_filename(filename):
    """Formats the filename: removes extra underscores and capitalizes first and middle names."""
    filename = filename.strip('_')
    parts = filename.split('_')
    formatted_parts = [part.capitalize() if part.isalpha() else part for part in parts]
    return '_'.join(formatted_parts)

def rename_edf_files(directory):
    """Renames EDF files in the directory."""
    edf_files = [f for f in os.listdir(directory) if f.endswith('.edf')]
    renamed_count = 0  # Counter for renamed files

    for file_name in tqdm(edf_files, desc="Renaming files", unit="file"):
        file_path = os.path.join(directory, file_name)
        patient_name, recording_date = get_edf_metadata(file_path)

        if patient_name and recording_date:
            formatted_patient_name = format_filename(patient_name)
            new_name = f"{formatted_patient_name}_{recording_date}.edf"
            new_file_path = os.path.join(directory, new_name)

            counter = 1
            while os.path.exists(new_file_path):
                new_name = f"{formatted_patient_name}_{recording_date}_{counter}.edf"
                new_file_path = os.path.join(directory, new_name)
                counter += 1

            os.rename(file_path, new_file_path)
            renamed_count += 1  # Increment the counter
        else:
            print(f"Failed to extract metadata for file {file_name}")

    return renamed_count  # Return the number of renamed files

def main():
    """Main function for renaming EDF files."""
    directory = input("Enter the path to the directory with EDF files: ").strip()
    if not os.path.isdir(directory):
        print("The specified directory does not exist.")
        return

    renamed_count = rename_edf_files(directory)
    print(f"Files renamed: {renamed_count}")

if __name__ == "__main__":
    main()