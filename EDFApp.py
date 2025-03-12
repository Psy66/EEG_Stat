import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from EDFProcessor import EDFProcessor
from EDFVisualizer import EDFVisualizer
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class EDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EDF File Manager")
        self.root.geometry("800x500")
        self.directory = ""
        self.processor = None
        self.visualizer = None
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
            self.processor = EDFProcessor(self.directory)
            self.visualizer = EDFVisualizer(self.directory)
            for btn in self.button_frame.winfo_children():
                if isinstance(btn, tk.Button) and btn["text"] != "Открыть папку":
                    btn.config(state=tk.NORMAL)

    def rename_files(self):
        """Переименование EDF-файлов."""
        self._execute_operation("процесс переименования файлов", self.processor.rename_edf_files)

    def find_duplicates(self):
        """Поиск и удаление дубликатов."""
        self._execute_operation("процесс поиска дубликатов", self._find_and_delete_duplicates)

    def check_corrupted(self):
        """Проверка на повреждения."""
        self._execute_operation("процесс проверки на повреждения", self.processor.find_and_delete_corrupted_edf)

    def generate_stats(self):
        """Генерация статистики."""
        self._execute_operation("процесс генерации статистики", self._generate_statistics_wrapper)

    def find_similar_time(self):
        """Поиск файлов с близким временем."""
        self._execute_operation("процесс поиска файлов с близким временем", self.processor.find_edf_with_similar_start_time)

    def generate_patient_table(self):
        """Генерация таблицы пациентов."""
        self._execute_operation("процесс создания таблицы пациентов", self.processor.generate_patient_table)

    def randomize_filenames(self):
        """Рандомизация имен файлов."""
        self._execute_operation("процесс рандомизации имен файлов", self._randomize_filenames_wrapper)

    def remove_patient_info(self):
        """Удаление информации о пациенте."""
        self._execute_operation("процесс удаления информации о пациенте", self.processor.remove_patient_info)

    def read_edf_info(self):
        """Чтение информации из EDF-файла."""
        self._execute_operation("процесс чтения информации из EDF-файла", self.processor.read_edf_info)

    def _execute_operation(self, operation_name, operation_func):
        """Выполняет операцию с обработкой ошибок."""
        if not self.directory:
            messagebox.showwarning("Ошибка", "Директория не выбрана.")
            return

        self.text_output.insert(tk.END, f"Начат {operation_name}...\n")
        self.text_output.update_idletasks()

        try:
            result = operation_func()
            self.text_output.insert(tk.END, f"{operation_name.capitalize()} завершен.\n")
            if result:
                self.text_output.insert(tk.END, f"Результат: {result}\n")
        except Exception as e:
            logging.error(f"Ошибка при выполнении {operation_name}: {e}")
            self.text_output.insert(tk.END, f"Ошибка: {e}\n")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def _find_and_delete_duplicates(self):
        """Поиск и удаление дубликатов."""
        duplicates = self.processor.find_duplicate_files()
        if duplicates:
            self.text_output.insert(tk.END, "Найдены дубликаты файлов:\n")
            for hash_val, paths in duplicates.items():
                self.text_output.insert(tk.END, f"Хэш: {hash_val}\n")
                for path in paths:
                    self.text_output.insert(tk.END, f"  {path}\n")
            self.processor.delete_duplicates(duplicates)
            return "Дубликаты удалены."
        return "Дубликатов не найдено."

    def _generate_statistics_wrapper(self):
        """Генерация и вывод статистики."""
        metadata_list = self.processor.analyze_directory()
        df, stats = self.processor.generate_statistics(metadata_list)
        self._display_statistics(stats)
        self.visualizer.visualize_statistics(df)
        return "Статистика сгенерирована и визуализирована."

    def _randomize_filenames_wrapper(self):
        """Рандомизация имен файлов."""
        return self.processor.randomize_filenames()

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