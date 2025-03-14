# generate_patient_table.py
import csv
import os
from tqdm import tqdm
from transliterate import translit

def extract_patient_name(filename):
    """Extracts the patient's name from the file name."""
    parts = filename.replace(".edf", "").split("_")
    if len(parts) >= 3:
        return " ".join(parts[:3])
    raise ValueError(f"Invalid file name: {filename}")

def generate_patient_table(directory, output_file):
    """Creates a CSV table with unique patient names in Cyrillic."""
    files = [f for f in os.listdir(directory) if f.endswith(".edf")]
    patient_names = set()

    for file in tqdm(files, desc="Processing files", unit="file"):
        try:
            name = extract_patient_name(file)
            # Transliterate the name from Latin to Cyrillic
            translated_name = translit(name, 'ru', reversed=True)
            patient_names.add(translated_name)
        except Exception as e:
            print(f"Error processing file {file}: {e}")

    sorted_names = sorted(patient_names)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Patient Name"])
        for name in sorted_names:
            writer.writerow([name])

def main():
    """Main function to generate the patient table."""
    directory = input("Enter the path to the directory containing EDF files: ").strip()
    output_file = "patient_table.csv"

    if not os.path.isdir(directory):
        print("The specified directory does not exist.")
    else:
        generate_patient_table(directory, output_file)
        print(f"The patient name table is saved to output/{output_file}.")

if __name__ == "__main__":
    main()