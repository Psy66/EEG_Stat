# edfinfo_chg.py
import os

def replace_patient_name_in_edf(edf_file_path):
    """
    Replaces the patient name in the EDF file with underscores (_) of the same length.
    The EDF file format has a fixed-length field for patient name at offset 8 (8th byte).
    """
    # Open the file in read-write mode (binary mode)
    with open(edf_file_path, 'r+b') as f:
        f.seek(8)  # Move to the start of the patientname field (8th byte)
        patientname = f.read(80).decode('ascii')  # Read the current patientname field

        # Split the patientname field into parts
        parts = patientname.split(' ', 3)  # Split by spaces, but no more than 3 times
        if len(parts) >= 3:
            # Keep the first three parts (UUID, gender, date of birth)
            new_patientname = ' '.join(parts[:3])
            # Replace the patient name with underscores (_) of the same length
            name_to_replace = parts[3].split('Startdate')[0]  # Remove "Startdate" and everything after
            new_patientname += ' ' + ('_' * len(name_to_replace))  # Replace the name with '_'
            # Add the remaining part (if any)
            if 'Startdate' in parts[3]:
                new_patientname += ' ' + parts[3].split('Startdate', 1)[1]
            # Pad to 80 characters
            new_patientname = new_patientname.ljust(80)
        else:
            # If the structure does not match the expected format, leave the field as is
            new_patientname = patientname

        # Write the new patientname field
        f.seek(8)
        f.write(new_patientname.encode('ascii'))

input_directory = input("Enter the path to the directory containing EDF files: ")

if not os.path.isdir(input_directory):
    print("The specified directory does not exist.")
else:
    edf_files = [f for f in os.listdir(input_directory) if f.endswith('.edf')]
    if not edf_files:
        print("There are no EDF files in the directory.")
    else:
        for file_name in edf_files:
            edf_file_path = os.path.join(input_directory, file_name)
            try:
                replace_patient_name_in_edf(edf_file_path)
                print(f"File {file_name} processed.")
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

        # Check the last processed file
        last_file = edf_files[-1]
        edf_file_path = os.path.join(input_directory, last_file)
        with open(edf_file_path, 'rb') as f:
            f.seek(8)
            patientname = f.read(80).decode('ascii').strip()
            print(f"\nInformation about the last processed file ({last_file}):")
            print(f"Patient name: {patientname}")