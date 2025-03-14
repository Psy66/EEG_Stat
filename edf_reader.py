# edf_reader.py
import os
from mne.io import read_raw_edf
from mne import find_events
from concurrent.futures import ThreadPoolExecutor, as_completed

def read_edf_metadata(file_path):
    """Reads metadata from an EDF file."""
    try:
        raw = read_raw_edf(file_path, preload=False)
        info = raw.info
        metadata = {
            'file_name': os.path.basename(file_path),
            'subject_info': info.get('subject_info', {}),
            'duration': raw.times[-1],
            'channels': info['ch_names'],
            'sfreq': info['sfreq'],
            'events': find_events(raw) if 'stim' in info['ch_names'] else None,  # Use find_events
            'meas_date': info.get('meas_date', None)
        }
        return metadata
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def analyze_directory(directory):
    """Analyzes all EDF files in the specified directory."""
    metadata_list = []
    edf_files = [os.path.join(directory, file_name) for file_name in os.listdir(directory) if file_name.endswith('.edf')]

    with ThreadPoolExecutor() as executor:
        # Start tasks in a thread pool
        future_to_file = {executor.submit(read_edf_metadata, file_path): file_path for file_path in edf_files}

        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                metadata = future.result()
                if metadata:
                    metadata_list.append(metadata)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    return metadata_list