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
        """Проверка существования директории."""
        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"Директория {self.directory} не существует.")
        return True

    def get_edf_metadata(self, file_path):
        """Извлекает метаданные из EDF-файла."""
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
            logging.error(f"Ошибка при чтении файла {file_path}: {e}")
            return None, None

    def format_filename(self, filename):
        """Форматирует имя файла: удаляет лишние подчеркивания и капитализирует имя и отчество."""
        filename = filename.strip('_')
        parts = filename.split('_')
        formatted_parts = [part.capitalize() if part.isalpha() else part for part in parts]
        return '_'.join(formatted_parts)

    def rename_edf_files(self):
        """Переименовывает EDF-файлы в директории."""
        edf_files = [f for f in os.listdir(self.directory) if f.endswith('.edf')]
        renamed_count = 0

        for file_name in tqdm(edf_files, desc="Переименование файлов", unit="file"):
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
                logging.warning(f"Не удалось извлечь метаданные для файла {file_name}")

        return renamed_count

    def read_edf_metadata(self, file_path):
        """Чтение метаданных из EDF-файла."""
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
            logging.error(f"Ошибка при чтении файла {file_path}: {e}")
            return None

    def analyze_directory(self):
        """Анализ всех EDF-файлов в указанной директории."""
        metadata_list = []
        for file_name in os.listdir(self.directory):
            if file_name.endswith('.edf'):
                file_path = os.path.join(self.directory, file_name)
                metadata = self.read_edf_metadata(file_path)
                if metadata:
                    metadata_list.append(metadata)
        return metadata_list

    def is_edf_corrupted(self, file_path):
        """Проверяет, повреждён ли EDF-файл."""
        try:
            raw = read_raw_edf(file_path, preload=False, verbose=False)
            return False
        except Exception as e:
            logging.error(f"Ошибка при чтении файла {file_path}: {e}")
            return True

    def find_and_delete_corrupted_edf(self):
        """Ищет и удаляет повреждённые EDF-файлы в указанной папке."""
        deleted_files = 0
        edf_files = [os.path.join(root, file) for root, _, files in os.walk(self.directory) for file in files if file.endswith(".edf")]

        for file_path in tqdm(edf_files, desc="Проверка файлов", unit="file"):
            if self.is_edf_corrupted(file_path):
                logging.warning(f"Файл повреждён: {file_path}")
                try:
                    os.remove(file_path)
                    logging.info(f"Файл удалён: {file_path}")
                    deleted_files += 1
                except Exception as e:
                    logging.error(f"Ошибка при удалении файла {file_path}: {e}")

        return deleted_files

    def get_edf_start_time(self, file_path):
        """Извлекает дату и время начала записи из EDF-файла."""
        try:
            raw = read_raw_edf(file_path, preload=False, verbose=False)
            start_datetime = raw.info['meas_date']
            if start_datetime:
                return start_datetime
            return None
        except Exception as e:
            logging.error(f"Ошибка при чтении файла {file_path}: {e}")
            return None

    def find_edf_with_similar_start_time(self, time_delta=timedelta(minutes=10)):
        """Ищет EDF-файлы с близким временем начала записи."""
        time_dict = defaultdict(list)
        edf_files = [os.path.join(root, file) for root, _, files in os.walk(self.directory) for file in files if file.lower().endswith('.edf')]

        for file_path in tqdm(edf_files, desc="Обработка файлов", unit="file"):
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
        """Вычисляет хэш файла для проверки содержимого."""
        hash_func = hashlib.new(hash_algorithm)
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def find_duplicate_files(self):
        """Ищет дубликаты файлов в указанной директории."""
        size_dict = defaultdict(list)

        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                size_dict[file_size].append(file_path)

        hash_dict = defaultdict(list)
        for size, paths in tqdm(size_dict.items(), desc="Проверка файлов", unit="group"):
            if len(paths) > 1:
                for path in paths:
                    file_hash = self.calculate_file_hash(path)
                    hash_dict[file_hash].append(path)

        duplicates = {hash_val: paths for hash_val, paths in hash_dict.items() if len(paths) > 1}
        return duplicates

    def delete_duplicates(self, duplicates):
        """Удаляет все дубликаты, кроме одного."""
        for hash_val, paths in duplicates.items():
            for path in tqdm(paths[1:], desc="Удаление дубликатов", unit="file"):
                try:
                    os.remove(path)
                    logging.info(f"Удален файл: {path}")
                except OSError as e:
                    logging.error(f"Ошибка при удалении файла {path}: {e}")

    def calculate_age(self, birthdate, recording_date):
        """Вычисляет возраст на момент записи."""
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
            logging.error(f"Ошибка при вычислении возраста: {e}")
            return None

    def generate_statistics(self, metadata_list):
        """Генерация описательной статистики по метаданным."""
        stats = defaultdict(list)
        for metadata in metadata_list:
            subject_info = metadata.get('subject_info', {})
            stats['file_name'].append(metadata['file_name'])
            stats['sex'].append(
                'Муж' if subject_info.get('sex') == 1 else 'Жен' if subject_info.get('sex') == 2 else 'Unknown')

            birthdate = subject_info.get('birthday')
            recording_date = metadata.get('meas_date')
            if birthdate and recording_date:
                age = self.calculate_age(birthdate, recording_date)
                if age is not None:
                    stats['age'].append(min(age, 60))  # Ограничение возраста до 60 лет

            stats['duration_minutes'].append(metadata['duration'] / 60)

        df = DataFrame(stats)
        descriptive_stats = {
            'sex_distribution': df['sex'].value_counts(),
            'age_distribution': df['age'].describe() if 'age' in df.columns else None,
            'duration_stats': df['duration_minutes'].describe()
        }
        return df, descriptive_stats

    def extract_patient_name(self, filename):
        """Извлекает имя пациента из имени файла."""
        parts = filename.replace(".edf", "").split("_")
        if len(parts) >= 3:
            return " ".join(parts[:3])
        raise ValueError(f"Некорректное имя файла: {filename}")

    def generate_patient_table(self, output_file="patient_table.csv"):
        """Создаёт таблицу CSV с уникальными именами пациентов на кириллице."""
        files = [f for f in os.listdir(self.directory) if f.endswith(".edf")]
        patient_names = set()

        for file in tqdm(files, desc="Обработка файлов", unit="file"):
            try:
                name = self.extract_patient_name(file)
                translated_name = translit(name, 'ru', reversed=True)
                patient_names.add(translated_name)
            except Exception as e:
                logging.error(f"Ошибка при обработке файла {file}: {e}")

        sorted_names = sorted(patient_names)
        output_path = os.path.join(self.output_dir, output_file)

        with open(output_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ФИО пациента"])
            for name in sorted_names:
                writer.writerow([name])

        return output_path

    def remove_patient_info(self):
        """Удаление информации о пациенте из EDF-файлов."""
        files = [f for f in os.listdir(self.directory) if f.endswith(".edf")]
        for file in files:
            file_path = os.path.join(self.directory, file)
            self._replace_patient_name_in_edf(file_path)
        return "Информация о пациенте удалена из всех EDF-файлов."

    def read_edf_info(self):
        """Чтение информации из EDF-файла."""
        files = [f for f in os.listdir(self.directory) if f.endswith(".edf")]
        if not files:
            return "В директории нет EDF-файлов."

        file_path = os.path.join(self.directory, files[0])
        raw = read_raw_edf(file_path, preload=True)
        info = raw.info

        result = f"Информация о файле: {file_path}\n"
        result += f"Частота дискретизации: {info['sfreq']} Гц\n"
        result += f"Количество каналов: {len(info['ch_names'])}\n"
        result += f"Продолжительность записи: {raw.times[-1]:.2f} секунд\n"

        return result

    @staticmethod
    def _replace_patient_name_in_edf(edf_file_path):
        """Заменяет имя пациента в EDF-файле на символы '_'."""
        with open(edf_file_path, 'r+b') as f:
            f.seek(8)
            patientname = f.read(80).decode('ascii')
            parts = patientname.split(' ', 3)
            if len(parts) >= 3:
                new_patientname = ' '.join(parts[:3])
                name_to_replace = parts[3].split('Startdate')[0]
                new_patientname += ' ' + ('_' * len(name_to_replace))
                if 'Startdate' in parts[3]:
                    new_patientname += ' ' + parts[3].split('Startdate', 1)[1]
                new_patientname = new_patientname.ljust(80)
            else:
                new_patientname = patientname
            f.seek(8)
            f.write(new_patientname.encode('ascii'))

    def randomize_filenames(self):
        """Рандомизация имен файлов."""
        files = [f for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))]
        used_codes = set()
        name_mapping = []

        for old_name in files:
            new_name = self._generate_unique_code(used_codes) + os.path.splitext(old_name)[1]
            os.rename(os.path.join(self.directory, old_name), os.path.join(self.directory, new_name))
            name_mapping.append((old_name, new_name))

        output_csv_path = os.path.join(self.directory, "name_mapping.csv")
        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Old Name', 'New Name'])
            writer.writerows(name_mapping)

        return f"Имена файлов рандомизированы. Таблица соответствия сохранена в {output_csv_path}"

    @staticmethod
    def _generate_unique_code(used_codes):
        """Генерация уникального 6-значного кода."""
        import random
        while True:
            code = ''.join(random.choices('0123456789', k=6))
            if code not in used_codes:
                used_codes.add(code)
                return code