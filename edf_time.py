# edf_time.py
import os
from collections import defaultdict
from datetime import timedelta
from mne.io import read_raw_edf
from tqdm import tqdm

def get_edf_start_time(file_path):
    """Извлекает дату и время начала записи из EDF-файла с помощью MNE."""
    try:
        raw = read_raw_edf(file_path, preload=False, verbose=False)
        start_datetime = raw.info['meas_date']
        if start_datetime:
            return start_datetime
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return None

def find_edf_with_similar_start_time(directory, time_delta=timedelta(minutes=10)):
    """Ищет EDF-файлы с близким временем начала записи (в пределах time_delta)."""
    time_dict = defaultdict(list)
    edf_files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.lower().endswith('.edf')]

    for file_path in tqdm(edf_files, desc="Обработка файлов", unit="file"):
        start_datetime = get_edf_start_time(file_path)
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

def main():
    """Основная функция для поиска файлов с близким временем начала записи."""
    directory = input("Введите путь к директории с EDF-файлами: ").strip()
    if not os.path.isdir(directory):
        print("Указанная директория не существует.")
        return

    similar_time_groups = find_edf_with_similar_start_time(directory)

    if similar_time_groups:
        print("Найдены EDF-файлы с близким временем начала записи (в пределах 10 минут):")
        for group in similar_time_groups:
            print(f"Группа файлов с близким временем начала:")
            for start_datetime, file_path in group:
                print(f"  Время: {start_datetime}, Файл: {file_path}")
    else:
        print("EDF-файлов с близким временем начала записи не найдено.")

if __name__ == "__main__":
    main()