import csv
import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tqdm import tqdm
from transliterate import translit
from edf_cur import find_and_delete_corrupted_edf
from edf_dubl_seek import delete_duplicates, find_duplicate_files
from edf_rename import rename_edf_files
from edf_time import find_edf_with_similar_start_time
from main import analyze_directory, generate_statistics, visualize_statistics
import mne
import random

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class EDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EDF File Manager")
        self.root.geometry("800x500")
        self.directory = ""
        self._setup_ui()

    def _setup_ui(self):
        """Инициализация интерфейса."""
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        buttons = [
            ("Открыть папку", self.select_directory, "Выберите папку с EDF-файлами"),
            ("Переименовать EDF", self.rename_files, "Переименовать EDF-файлы по метаданным"),
            ("Удалить поврежденные", self.check_corrupted, "Удалить поврежденные EDF-файлы"),
            ("Удалить дубликаты", self.find_duplicates, "Найти и удалить дубликаты EDF-файлов"),
            ("Найти похожие", self.find_similar_time, "Найти EDF-файлы с близким временем начала записи"),
            ("Сгенерировать статистику", self.generate_stats, "Сгенерировать статистику по EDF-файлам"),
            ("Создать таблицу пациентов", self.generate_patient_table, "Создать CSV-таблицу с именами пациентов"),
            ("Рандомизировать названия", self.randomize_filenames, "Рандомизировать имена файлов в папке"),
            ("Удалить patientinfo", self.remove_patient_info, "Удалить информацию о пациенте из EDF-файлов"),
            ("Прочитать info EDF", self.read_edf_info, "Прочитать и отобразить информацию из EDF-файла"),
            ("Выход", self.root.quit, "Закрыть программу")
        ]

        for idx, (text, command, tooltip) in enumerate(buttons):
            btn = tk.Button(self.button_frame, text=text, command=command, state=tk.DISABLED if idx > 0 else tk.NORMAL)
            btn.grid(row=idx // 3, column=idx % 3, padx=5, pady=5)
            self._create_tooltip(btn, tooltip)

        self.text_output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=90, height=20)
        self.text_output.pack(pady=10)

    def _create_tooltip(self, widget, text):
        """Создает всплывающую подсказку для виджета."""
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry("+0+0")
        tooltip.withdraw()

        label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

        widget.bind("<Enter>", lambda e: self._show_tooltip(tooltip, widget))
        widget.bind("<Leave>", lambda e: tooltip.withdraw())

    @staticmethod
    def _show_tooltip(tooltip, widget):
        """Показывает всплывающую подсказку."""
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        tooltip.wm_geometry(f"+{x}+{y}")
        tooltip.deiconify()

    def select_directory(self):
        """Выбор директории с EDF-файлами."""
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.text_output.insert(tk.END, f"Выбрана директория: {self.directory}\n")
            for btn in self.button_frame.winfo_children():
                if isinstance(btn, tk.Button) and btn["text"] != "Открыть папку":
                    btn.config(state=tk.NORMAL)

    def rename_files(self):
        """Переименование EDF-файлов."""
        self._execute_operation("процесс переименования файлов", rename_edf_files)

    def find_duplicates(self):
        """Поиск и удаление дубликатов."""
        self._execute_operation("процесс поиска дубликатов", self._find_and_delete_duplicates)

    def check_corrupted(self):
        """Проверка на повреждения."""
        self._execute_operation("процесс проверки на повреждения", find_and_delete_corrupted_edf)

    def generate_stats(self):
        """Генерация статистики."""
        self._execute_operation("процесс генерации статистики", self._generate_statistics_wrapper)

    def find_similar_time(self):
        """Поиск файлов с близким временем."""
        self._execute_operation("процесс поиска файлов с близким временем", find_edf_with_similar_start_time)

    def generate_patient_table(self):
        """Генерация таблицы пациентов."""
        self._execute_operation("процесс создания таблицы пациентов", self._generate_patient_table_wrapper)

    def randomize_filenames(self):
        """Рандомизация имен файлов."""
        self._execute_operation("процесс рандомизации имен файлов", self._randomize_filenames_wrapper)

    def remove_patient_info(self):
        """Удаление информации о пациенте."""
        self._execute_operation("процесс удаления информации о пациенте", self._remove_patient_info_wrapper)

    def read_edf_info(self):
        """Чтение информации из EDF-файла."""
        self._execute_operation("процесс чтения информации из EDF-файла", self._read_edf_info_wrapper)

    def _execute_operation(self, operation_name, operation_func):
        """Выполняет операцию с обработкой ошибок."""
        if not self.directory:
            messagebox.showwarning("Ошибка", "Директория не выбрана.")
            return

        self.text_output.insert(tk.END, f"Начат {operation_name}...\n")
        self.text_output.update_idletasks()

        try:
            result = operation_func(self.directory)
            self.text_output.insert(tk.END, f"{operation_name.capitalize()} завершен.\n")
            if result:
                self.text_output.insert(tk.END, f"Результат: {result}\n")
        except Exception as e:
            logging.error(f"Ошибка при выполнении {operation_name}: {e}")
            self.text_output.insert(tk.END, f"Ошибка: {e}\n")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def _find_and_delete_duplicates(self, directory):
        """Поиск и удаление дубликатов."""
        duplicates = find_duplicate_files(directory)
        if duplicates:
            self.text_output.insert(tk.END, "Найдены дубликаты файлов:\n")
            for hash_val, paths in duplicates.items():
                self.text_output.insert(tk.END, f"Хэш: {hash_val}\n")
                for path in paths:
                    self.text_output.insert(tk.END, f"  {path}\n")
            delete_duplicates(duplicates)
            return "Дубликаты удалены."
        return "Дубликатов не найдено."

    def _generate_statistics_wrapper(self, directory):
        """Генерация и вывод статистики."""
        output_directory = os.path.join(directory, "output")
        os.makedirs(output_directory, exist_ok=True)

        try:
            metadata_list = analyze_directory(directory)
            df, stats = generate_statistics(metadata_list)
            self._display_statistics(stats)
            output_csv_path = os.path.join(output_directory, 'edf_metadata_stats.csv')
            df.to_csv(output_csv_path, index=False)
            visualize_statistics(df, output_directory)
            return f"Статистика сохранена в {output_csv_path}"
        except Exception as e:
            logging.error(f"Ошибка при генерации статистики: {e}")
            raise

    def _generate_patient_table_wrapper(self, directory):
        """Генерация таблицы пациентов."""
        output_file = "patient_table.csv"
        output_directory = os.path.join(directory, "output")
        os.makedirs(output_directory, exist_ok=True)
        output_path = os.path.join(output_directory, output_file)

        try:
            files = [f for f in os.listdir(directory) if f.endswith(".edf")]
            patient_names = set()

            for file in tqdm(files, desc="Обработка файлов", unit="file"):
                try:
                    name = self._extract_patient_name(file)
                    translated_name = translit(name, 'ru')
                    patient_names.add(translated_name)
                except Exception as e:
                    self.text_output.insert(tk.END, f"Ошибка при обработке файла {file}: {e}\n")

            sorted_names = sorted(patient_names)

            with open(output_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ФИО пациента"])
                for name in sorted_names:
                    writer.writerow([name])

            return f"Таблица пациентов сохранена в {output_path}"
        except Exception as e:
            logging.error(f"Ошибка при генерации таблицы пациентов: {e}")
            raise

    def _randomize_filenames_wrapper(self, directory):
        """Рандомизация имен файлов."""
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        used_codes = set()
        name_mapping = []

        for old_name in files:
            new_name = self._generate_unique_code(used_codes) + os.path.splitext(old_name)[1]
            os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
            name_mapping.append((old_name, new_name))

        output_csv_path = os.path.join(directory, "name_mapping.csv")
        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Old Name', 'New Name'])
            writer.writerows(name_mapping)

        return f"Имена файлов рандомизированы. Таблица соответствия сохранена в {output_csv_path}"

    def _remove_patient_info_wrapper(self, directory):
        """Удаление информации о пациенте из EDF-файлов."""
        files = [f for f in os.listdir(directory) if f.endswith(".edf")]
        for file in files:
            file_path = os.path.join(directory, file)
            self._replace_patient_name_in_edf(file_path)
        return "Информация о пациенте удалена из всех EDF-файлов."

    def _read_edf_info_wrapper(self, directory):
        """Чтение информации из EDF-файла."""
        files = [f for f in os.listdir(directory) if f.endswith(".edf")]
        if not files:
            return "В директории нет EDF-файлов."

        file_path = os.path.join(directory, files[0])
        raw = mne.io.read_raw_edf(file_path, preload=True)
        info = raw.info

        result = f"Информация о файле: {file_path}\n"
        result += f"Частота дискретизации: {info['sfreq']} Гц\n"
        result += f"Количество каналов: {len(info['ch_names'])}\n"
        result += f"Продолжительность записи: {raw.times[-1]:.2f} секунд\n"

        self.text_output.insert(tk.END, result)
        return "Информация прочитана и отображена."

    @staticmethod
    def _generate_unique_code(used_codes):
        """Генерация уникального 6-значного кода."""
        while True:
            code = ''.join(random.choices('0123456789', k=6))
            if code not in used_codes:
                used_codes.add(code)
                return code

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

    @staticmethod
    def _extract_patient_name(filename):
        """Извлекает имя пациента из имени файла."""
        parts = filename.replace(".edf", "").split("_")
        if len(parts) >= 3:
            return " ".join(parts[:3])
        raise ValueError(f"Некорректное имя файла: {filename}")

    def _display_statistics(self, stats):
        """Отображает статистику в текстовом поле."""
        self.text_output.insert(tk.END, "Описательная статистика:\n")
        if 'sex_distribution' in stats and stats['sex_distribution'] is not None:
            self.text_output.insert(tk.END, "Распределение по полу:\n")
            for sex, count in stats['sex_distribution'].items():
                self.text_output.insert(tk.END, f"  {sex}: {count}\n")
        if 'age_distribution' in stats and stats['age_distribution'] is not None:
            self.text_output.insert(tk.END, "\nРаспределение по возрасту:\n")
            age_stats = stats['age_distribution']
            self.text_output.insert(tk.END, f"  Количество: {int(age_stats['count'])}\n")
            self.text_output.insert(tk.END, f"  Средний возраст: {age_stats['mean']:.2f} лет\n")
            self.text_output.insert(tk.END, f"  Минимальный возраст: {age_stats['min']} лет\n")
            self.text_output.insert(tk.END, f"  Максимальный возраст: {age_stats['max']} лет\n")
        if 'duration_stats' in stats and stats['duration_stats'] is not None:
            self.text_output.insert(tk.END, "\nСтатистика по длительности записи (минуты):\n")
            duration_stats = stats['duration_stats']
            self.text_output.insert(tk.END, f"  Средняя длительность: {duration_stats['mean']:.2f} мин\n")
            self.text_output.insert(tk.END, f"  Минимальная длительность: {duration_stats['min']:.2f} мин\n")
            self.text_output.insert(tk.END, f"  Максимальная длительность: {duration_stats['max']:.2f} мин\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = EDFApp(root)
    root.mainloop()