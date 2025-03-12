# edf_info.py
import mne
import os

def print_edf_file_info(edf_file_path):
    # Чтение EDF-файла
    raw = mne.io.read_raw_edf(edf_file_path, preload=True)

    # Получение информации о файле
    info = raw.info

    # Вывод общей информации
    print("=" * 50)
    print(f"Информация о файле: {edf_file_path}")
    print("=" * 50)

    # Информация о пациенте
    subject_info = info.get('subject_info', {})
    print("\nИнформация о пациенте:")
    print(f"  Имя пациента: {subject_info.get('his_id', 'Не указано')}")
    print(f"  Пол: {subject_info.get('sex', 'Не указан')}")
    print(f"  Дата рождения: {subject_info.get('birthday', 'Не указана')}")
    print(f"  Дополнительные данные: {subject_info.get('comments', 'Не указаны')}")

    # Информация о записи
    print("\nИнформация о записи:")
    print(f"  Дата записи: {info.get('meas_date', 'Не указана')}")
    print(f"  Частота дискретизации: {info['sfreq']} Гц")
    print(f"  Количество каналов: {len(info['ch_names'])}")

    # Список каналов
    print("\nСписок каналов:")
    for i, ch_name in enumerate(info['ch_names'], 1):
        print(f"  {i}. {ch_name}")

    # Дополнительная информация
    print("\nДополнительная информация:")
    print(f"  Продолжительность записи: {raw.times[-1]:.2f} секунд")
    print(f"  Размер файла: {os.path.getsize(edf_file_path) / 1024 / 1024:.2f} МБ")

# Пример использования
edf_file_path = input("Введите путь к EDF-файлу: ").strip('"')  # Удаляем кавычки
if os.path.isfile(edf_file_path):
    print_edf_file_info(edf_file_path)
else:
    print("Файл не найден.")