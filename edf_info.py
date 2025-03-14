# edf_info.py
import mne
import os

def print_edf_file_info(edf_file_path):
    # Read the EDF file
    raw = mne.io.read_raw_edf(edf_file_path, preload=True)

    # Get file information
    info = raw.info

    # Print general information
    print("=" * 50)
    print(f"File Information: {edf_file_path}")
    print("=" * 50)

    # Patient information
    subject_info = info.get('subject_info', {})
    print("\nPatient Information:")
    print(f"  Patient Name: {subject_info.get('his_id', 'Not specified')}")
    print(f"  Gender: {subject_info.get('sex', 'Not specified')}")
    print(f"  Date of Birth: {subject_info.get('birthday', 'Not specified')}")
    print(f"  Additional Data: {subject_info.get('comments', 'Not specified')}")

    # Recording information
    print("\nRecording Information:")
    print(f"  Recording Date: {info.get('meas_date', 'Not specified')}")
    print(f"  Sampling Frequency: {info['sfreq']} Hz")
    print(f"  Number of Channels: {len(info['ch_names'])}")

    # List of channels
    print("\nList of Channels:")
    for i, ch_name in enumerate(info['ch_names'], 1):
        print(f"  {i}. {ch_name}")

    # Additional information
    print("\nAdditional Information:")
    print(f"  Recording Duration: {raw.times[-1]:.2f} seconds")
    print(f"  File Size: {os.path.getsize(edf_file_path) / 1024 / 1024:.2f} MB")

# Example usage
edf_file_path = input("Enter the path to the EDF file: ").strip('"')
if os.path.isfile(edf_file_path):
    print_edf_file_info(edf_file_path)
else:
    print("File not found.")