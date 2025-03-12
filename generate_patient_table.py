# generate_patient_table.py
import csv
import os
from tqdm import tqdm
from transliterate import translit

def extract_patient_name(filename):
    """Извлекает имя пациента из имени файла."""
    parts = filename.replace(".edf", "").split("_")
    if len(parts) >= 3:
        return " ".join(parts[:3])
    raise ValueError(f"Некорректное имя файла: {filename}")

def generate_patient_table(directory, output_file):
    """Создаёт таблицу CSV с уникальными именами пациентов на кириллице."""
    files = [f for f in os.listdir(directory) if f.endswith(".edf")]
    patient_names = set()

    for file in tqdm(files, desc="Обработка файлов", unit="file"):
        try:
            name = extract_patient_name(file)
            # Транслитерируем имя с латиницы на кириллицу
            translated_name = translit(name, 'ru', reversed=True)
            patient_names.add(translated_name)
        except Exception as e:
            print(f"Ошибка при обработке файла {file}: {e}")

    sorted_names = sorted(patient_names)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ФИО пациента"])
        for name in sorted_names:
            writer.writerow([name])

def main():
    """Основная функция для генерации таблицы пациентов."""
    directory = input("Введите путь к директории с EDF-файлами: ").strip()
    output_file = "patient_table.csv"

    if not os.path.isdir(directory):
        print("Указанная директория не существует.")
    else:
        generate_patient_table(directory, output_file)
        print(f"Таблица с именами пациентов сохранена в файл output/{output_file}.")

if __name__ == "__main__":
    main()