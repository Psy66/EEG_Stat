# edf_rename.py
import os
from mne.io import read_raw_edf
from tqdm import tqdm

def get_edf_metadata(file_path):
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
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return None, None

def format_filename(filename):
    """Форматирует имя файла: удаляет лишние подчеркивания и капитализирует имя и отчество."""
    filename = filename.strip('_')
    parts = filename.split('_')
    formatted_parts = [part.capitalize() if part.isalpha() else part for part in parts]
    return '_'.join(formatted_parts)

def rename_edf_files(directory):
    """Переименовывает EDF-файлы в директории."""
    edf_files = [f for f in os.listdir(directory) if f.endswith('.edf')]
    renamed_count = 0  # Счётчик переименованных файлов

    for file_name in tqdm(edf_files, desc="Переименование файлов", unit="file"):
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
            renamed_count += 1  # Увеличиваем счётчик
        else:
            print(f"Не удалось извлечь метаданные для файла {file_name}")

    return renamed_count  # Возвращаем количество переименованных файлов

def main():
    """Основная функция для переименования EDF-файлов."""
    directory = input("Введите путь к директории с EDF-файлами: ").strip()
    if not os.path.isdir(directory):
        print("Указанная директория не существует.")
        return

    renamed_count = rename_edf_files(directory)
    print(f"Переименовано файлов: {renamed_count}")

if __name__ == "__main__":
    main()