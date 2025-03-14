# EDFProcessor.py
import os
import hashlib
import csv
from collections import defaultdict
from datetime import timedelta
from dateutil.parser import parse
from tqdm import tqdm
from mne.io import read_raw_edf
from mne import find_events
from pandas import DataFrame
from transliterate import translit
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class EDFProcessor:
    def __init__(self, directory):
        self.directory = directory
        self.output_dir = os.path.join(self.directory, "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def check_directory(self):
        """Checks if the directory exists."""
        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"Directory {self.directory} does not exist.")
        return True

    def get_edf_metadata(self, file_path):
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
            logging.error(f"Error reading file {file_path}: {e}")
            return None, None

    def format_filename(self, filename):
        """Formats the file name: removes extra underscores and capitalizes first and middle names."""
        filename = filename.strip('_')
        parts = filename.split('_')
        formatted_parts = [part.capitalize() if part.isalpha() else part for part in parts]
        return '_'.join(formatted_parts)

    def rename_edf_files(self):
        """Renames EDF files in the directory."""
        edf_files = [f for f in os.listdir(self.directory) if f.endswith('.edf')]
        renamed_count = 0

        for file_name in tqdm(edf_files, desc="Renaming files", unit="file"):
            file_path = os.path.join(self.directory, file_name)
            patient_name, recording_date = self.get_edf_metadata(file_path)

            if patient_name and recording_date:
                formatted_patient_name = self.format_filename(patient_name)
                new_name = f"{formatted_patient_name}_{recording_date}.edf"
                new_file_path = os.path.join(self.directory, new_name)

                counter = 1
                while os.path.exists(new_file_path):
                    new_name = f"{formatted_patient_name}_{recording_date}_{counter}.edf"
                    new_file_path = os.path.join(self.directory, new_name)
                    counter += 1

                os.rename(file_path, new_file_path)
                renamed_count += 1
            else:
                logging.warning(f"Failed to extract metadata for file {file_name}")

        return renamed_count

    def read_edf_metadata(self, file_path):
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
                'events': find_events(raw) if 'stim' in info['ch_names'] else None,
                'meas_date': info.get('meas_date', None)
            }
            return metadata
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return None

    def analyze_directory(self):
        """Analyzes all EDF files in the specified directory."""
        metadata_list = []
        for file_name in os.listdir(self.directory):
            if file_name.endswith('.edf'):
                file_path = os.path.join(self.directory, file_name)
                metadata = self.read_edf_metadata(file_path)
                if metadata:
                    metadata_list.append(metadata)
        return metadata_list

    def is_edf_corrupted(self, file_path):
        """Checks if an EDF file is corrupted."""
        try:
            raw = read_raw_edf(file_path, preload=False, verbose=False)
            return False
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return True

    def find_and_delete_corrupted_edf(self):
        """Finds and deletes corrupted EDF files in the specified folder."""
        deleted_files = 0
        edf_files = [os.path.join(root, file) for root, _, files in os.walk(self.directory) for file in files if file.endswith(".edf")]

        for file_path in tqdm(edf_files, desc="Checking files", unit="file"):
            if self.is_edf_corrupted(file_path):
                logging.warning(f"Corrupted file: {file_path}")
                try:
                    os.remove(file_path)
                    logging.info(f"File deleted: {file_path}")
                    deleted_files += 1
                except Exception as e:
                    logging.error(f"Error deleting file {file_path}: {e}")

        return deleted_files

    def get_edf_start_time(self, file_path):
        """Extracts the recording start time from an EDF file."""
        try:
            raw = read_raw_edf(file_path, preload=False, verbose=False)
            start_datetime = raw.info['meas_date']
            if start_datetime:
                return start_datetime
            return None
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return None

    def find_edf_with_similar_start_time(self, time_delta=timedelta(minutes=10)):
        """Finds EDF files with similar start times."""
        time_dict = defaultdict(list)
        edf_files = [os.path.join(root, file) for root, _, files in os.walk(self.directory) for file in files if file.lower().endswith('.edf')]

        for file_path in tqdm(edf_files, desc="Processing files", unit="file"):
            start_datetime = self.get_edf_start_time(file_path)
            if start_datetime:
                rounded_time = start_datetime - timedelta(minutes=start_datetime.minute % 10)
                time_dict[rounded_time].append((start_datetime, file_path))

        similar_time_groups = []
        for rounded_time, files in time_dict.items():
            if len(files) > 1:
                files.sort()
                for i in range(1, len(files)):
                    if files[i][0] - files[i - 1][0] <= time_delta:
                        similar_time_groups.append(files)
                        break

        return similar_time_groups

    def calculate_file_hash(self, file_path, hash_algorithm="md5", chunk_size=8192):
        """Calculates the file hash for content verification."""
        hash_func = hashlib.new(hash_algorithm)
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def find_duplicate_files(self):
        """Finds duplicate files in the specified directory."""
        size_dict = defaultdict(list)

        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                size_dict[file_size].append(file_path)

        hash_dict = defaultdict(list)
        for size, paths in tqdm(size_dict.items(), desc="Checking files", unit="group"):
            if len(paths) > 1:
                for path in paths:
                    file_hash = self.calculate_file_hash(path)
                    hash_dict[file_hash].append(path)

        duplicates = {hash_val: paths for hash_val, paths in hash_dict.items() if len(paths) > 1}
        return duplicates

    def delete_duplicates(self, duplicates):
        """Deletes all duplicates except one."""
        for hash_val, paths in duplicates.items():
            for path in tqdm(paths[1:], desc="Deleting duplicates", unit="file"):
                try:
                    os.remove(path)
                    logging.info(f"Deleted file: {path}")
                except OSError as e:
                    logging.error(f"Error deleting file {path}: {e}")

    def calculate_age(self, birthdate, recording_date):
        """Calculates the age at the time of recording."""
        try:
            if isinstance(birthdate, str):
                birthdate = parse(birthdate)
            if isinstance(recording_date, str):
                recording_date = parse(recording_date)
            if hasattr(recording_date, 'tzinfo') and recording_date.tzinfo is not None:
                recording_date = recording_date.replace(tzinfo=None)
            age = recording_date.year - birthdate.year
            if (recording_date.month, recording_date.day) < (birthdate.month, birthdate.day):
                age -= 1
            return age
        except Exception as e:
            logging.error(f"Error calculating age: {e}")
            return None

    def generate_statistics(self, metadata_list):
        """Generates descriptive statistics from metadata."""
        stats = defaultdict(list)
        for metadata in metadata_list:
            subject_info = metadata.get('subject_info', {})
            stats['file_name'].append(metadata['file_name'])
            stats['sex'].append(
                'Male' if subject_info.get('sex') == 1 else 'Female' if subject_info.get('sex') == 2 else 'Unknown')

            birthdate = subject_info.get('birthday')
            recording_date = metadata.get('meas_date')
            if birthdate and recording_date:
                age = self.calculate_age(birthdate, recording_date)
                if age is not None:
                    stats['age'].append(min(age, 60))  # Limit age to 60 years

            stats['duration_minutes'].append(metadata['duration'] / 60)

        df = DataFrame(stats)
        descriptive_stats = {
            'sex_distribution': df['sex'].value_counts(),
            'age_distribution': df['age'].describe() if 'age' in df.columns else None,
            'duration_stats': df['duration_minutes'].describe()
        }
        return df, descriptive_stats

    def visualize_statistics(self, df):
        """Visualizes the statistics."""
        if 'sex' in df.columns:
            figure(figsize=(8, 6))
            countplot(data=df, x='sex')
            title('Sex Distribution')
            savefig(os.path.join(self.output_dir, 'sex_distribution.png'))
            close()

        if 'age' in df.columns:
            age_data = df[df['age'].apply(lambda x: isinstance(x, (int, float)))]
            if not age_data.empty:
                figure(figsize=(8, 6))
                histplot(data=age_data, x='age', bins=20, kde=True)
                title('Age Distribution')
                savefig(os.path.join(self.output_dir, 'age_distribution.png'))
                close()

        if 'duration_minutes' in df.columns:
            figure(figsize=(8, 6))
            histplot(data=df, x='duration_minutes', bins=20, kde=True)
            title('Recording Duration (minutes)')
            savefig(os.path.join(self.output_dir, 'duration_distribution.png'))
            close()

    def export_statistics(self, df, descriptive_stats):
        """Exports the statistics to CSV and Excel files."""
        os.makedirs(self.output_dir, exist_ok=True)
        df.to_csv(os.path.join(self.output_dir, 'edf_metadata.csv'), index=False)
        df.to_excel(os.path.join(self.output_dir, 'edf_metadata.xlsx'), index=False)

        with open(os.path.join(self.output_dir, 'descriptive_stats.txt'), 'w') as f:
            f.write("Descriptive Statistics:\n")
            f.write(f"Sex Distribution:\n{descriptive_stats['sex_distribution']}\n")
            f.write(f"Age Distribution:\n{descriptive_stats['age_distribution']}\n")
            f.write(f"Duration Statistics:\n{descriptive_stats['duration_stats']}\n")

        logging.info(f"Exported statistics to {self.output_dir}")

    def run(self):
        """Runs the EDF processing pipeline."""
        self.check_directory()
        metadata_list = self.analyze_directory()
        df, descriptive_stats = self.generate_statistics(metadata_list)
        self.visualize_statistics(df)
        self.export_statistics(df, descriptive_stats)
        logging.info("EDF processing completed.")

if __name__ == "__main__":
    directory = input("Enter the path to the directory containing EDF files: ").strip()
    processor = EDFProcessor(directory)
    processor.run()