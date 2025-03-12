# edf_dubl_seek.py
import hashlib
import os
from collections import defaultdict

from tqdm import tqdm

def calculate_file_hash(file_path, hash_algorithm="md5", chunk_size=8192):
    """Вычисляет хэш файла для проверки содержимого."""
    hash_func = hashlib.new(hash_algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def find_duplicate_files(directory):
    """Ищет дубликаты файлов в указанной директории."""
    size_dict = defaultdict(list)

    # Сбор файлов по размеру
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            size_dict[file_size].append(file_path)

    hash_dict = defaultdict(list)

    # Проверка хэша для файлов с одинаковым размером
    for size, paths in tqdm(size_dict.items(), desc="Проверка файлов", unit="group"):
        if len(paths) > 1:
            for path in paths:
                file_hash = calculate_file_hash(path)
                hash_dict[file_hash].append(path)

    # Фильтрация дубликатов
    duplicates = {hash_val: paths for hash_val, paths in hash_dict.items() if len(paths) > 1}

    return duplicates

def delete_duplicates(duplicates):
    """Удаляет все дубликаты, кроме одного."""
    for hash_val, paths in duplicates.items():
        for path in tqdm(paths[1:], desc="Удаление дубликатов", unit="file"):
            try:
                os.remove(path)
                print(f"Удален файл: {path}")
            except OSError as e:
                print(f"Ошибка при удалении файла {path}: {e}")

def main():
    """Основная функция для поиска и удаления дубликатов."""
    directory = input("Введите путь к директории: ")
    duplicates = find_duplicate_files(directory)

    if duplicates:
        print("Найдены дубликаты файлов (совпадают по содержимому):")
        for hash_val, paths in duplicates.items():
            print(f"Хэш: {hash_val}")
            for path in paths:
                print(f"  {path}")

        delete_duplicates(duplicates)
    else:
        print("Дубликатов файлов не найдено.")

if __name__ == "__main__":
    main()