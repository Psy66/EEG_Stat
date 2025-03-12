# main.py
import os

from edf_reader import analyze_directory
from eeg_statistics import generate_statistics, visualize_statistics
from utils import check_directory

def main():
    """Основная функция для анализа и визуализации данных."""
    input_directory = input("Введите путь к папке с EDF-файлами: ").strip()
    output_directory = os.path.join(input_directory, "output")

    try:
        check_directory(input_directory)
        os.makedirs(output_directory, exist_ok=True)

        metadata_list = analyze_directory(input_directory)
        df, stats = generate_statistics(metadata_list)

        print("Описательная статистика:")
        print(stats)

        output_csv_path = os.path.join(output_directory, 'edf_metadata_stats.csv')
        df.to_csv(output_csv_path, index=False)
        print(f"Статистика сохранена в {output_csv_path}")

        visualize_statistics(df, output_directory)
        print(f"Графики сохранены в {output_directory}")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()