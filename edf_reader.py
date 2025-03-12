# edf_reader.py
import os
from mne.io import read_raw_edf
from mne import find_events
from concurrent.futures import ThreadPoolExecutor, as_completed

def read_edf_metadata(file_path):
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
            'events': find_events(raw) if 'stim' in info['ch_names'] else None,  # Используем find_events
            'meas_date': info.get('meas_date', None)
        }
        return metadata
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return None

def analyze_directory(directory):
    """Анализ всех EDF-файлов в указанной директории."""
    metadata_list = []
    edf_files = [os.path.join(directory, file_name) for file_name in os.listdir(directory) if file_name.endswith('.edf')]

    with ThreadPoolExecutor() as executor:
        # Запускаем задачи в пуле потоков
        future_to_file = {executor.submit(read_edf_metadata, file_path): file_path for file_path in edf_files}

        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                metadata = future.result()
                if metadata:
                    metadata_list.append(metadata)
            except Exception as e:
                print(f"Ошибка при обработке файла {file_path}: {e}")

    return metadata_list