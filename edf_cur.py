# edf_cur.py
import os
from mne.io import read_raw_edf
from tqdm import tqdm

def is_edf_corrupted(file_path):
    """Проверяет, повреждён ли EDF-файл с помощью MNE."""
    try:
        raw = read_raw_edf(file_path, preload=False, verbose=False)  # Используем только read_raw_edf
        return False
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return True

def find_and_delete_corrupted_edf(directory):
    """Ищет и удаляет повреждённые EDF-файлы в указанной папке."""
    deleted_files = 0
    edf_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".edf"):
                edf_files.append(os.path.join(root, file))

    for file_path in tqdm(edf_files, desc="Проверка файлов", unit="file"):
        if is_edf_corrupted(file_path):
            print(f"Файл повреждён: {file_path}")
            try:
                os.remove(file_path)
                print(f"Файл удалён: {file_path}")
                deleted_files += 1
            except Exception as e:
                print(f"Ошибка при удалении файла {file_path}: {e}")

    print(f"Удалено повреждённых файлов: {deleted_files}")

if __name__ == "__main__":
    directory = input("Введите путь к папке: ").strip()

    if os.path.isdir(directory):
        find_and_delete_corrupted_edf(directory)
    else:
        print("Указанная папка не существует.")