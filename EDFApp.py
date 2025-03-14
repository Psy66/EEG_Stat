# EDFApp.py
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
        """Initializes the user interface."""
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        buttons = [
            ("Open Folder", self.select_directory, "Select a folder containing EDF files"),
            ("Rename EDF", self.rename_files, "Rename EDF files based on metadata"),
            ("Delete Corrupted", self.check_corrupted, "Delete corrupted EDF files"),
            ("Delete Duplicates", self.find_duplicates, "Find and delete duplicate EDF files"),
            ("Find Similar", self.find_similar_time, "Find EDF files with similar start times"),
            ("Generate Statistics", self.generate_stats, "Generate statistics for EDF files"),
            ("Create Patient Table", self.generate_patient_table, "Create a CSV table with patient names"),
            ("Randomize Filenames", self.randomize_filenames, "Randomize file names in the folder"),
            ("Remove Patient Info", self.remove_patient_info, "Remove patient information from EDF files"),
            ("Read EDF Info", self.read_edf_info, "Read and display information from EDF file"),
            ("Exit", self.root.quit, "Close the program")
        ]

        for idx, (text, command, tooltip) in enumerate(buttons):
            btn = tk.Button(self.button_frame, text=text, command=command, state=tk.DISABLED if idx > 0 else tk.NORMAL)
            btn.grid(row=idx // 3, column=idx % 3, padx=5, pady=5)
            self._create_tooltip(btn, tooltip)

        self.text_output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=90, height=20)
        self.text_output.pack(pady=10)

    def _create_tooltip(self, widget, text):
        """Creates a tooltip for the widget."""
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
        """Shows the tooltip."""
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        tooltip.wm_geometry(f"+{x}+{y}")
        tooltip.deiconify()

    def select_directory(self):
        """Selects a directory containing EDF files."""
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.text_output.insert(tk.END, f"Selected directory: {self.directory}\n")
            self.processor = EDFProcessor(self.directory)
            self.visualizer = EDFVisualizer(self.directory)
            for btn in self.button_frame.winfo_children():
                if isinstance(btn, tk.Button) and btn["text"] != "Open Folder":
                    btn.config(state=tk.NORMAL)

    def rename_files(self):
        """Renames EDF files."""
        self._execute_operation("file renaming process", self.processor.rename_edf_files)

    def find_duplicates(self):
        """Finds and deletes duplicates."""
        self._execute_operation("duplicate search process", self._find_and_delete_duplicates)

    def check_corrupted(self):
        """Checks for corrupted files."""
        self._execute_operation("corrupted file check process", self.processor.find_and_delete_corrupted_edf)

    def generate_stats(self):
        """Generates statistics."""
        self._execute_operation("statistics generation process", self._generate_statistics_wrapper)

    def find_similar_time(self):
        """Finds files with similar start times."""
        self._execute_operation("similar time search process", self.processor.find_edf_with_similar_start_time)

    def generate_patient_table(self):
        """Generates a patient table."""
        self._execute_operation("patient table creation process", self.processor.generate_patient_table)

    def randomize_filenames(self):
        """Randomizes file names."""
        self._execute_operation("filename randomization process", self._randomize_filenames_wrapper)

    def remove_patient_info(self):
        """Removes patient information."""
        self._execute_operation("patient information removal process", self.processor.remove_patient_info)

    def read_edf_info(self):
        """Reads EDF file information."""
        self._execute_operation("EDF file information reading process", self.processor.read_edf_info)

    def _execute_operation(self, operation_name, operation_func):
        """Executes an operation with error handling."""
        if not self.directory:
            messagebox.showwarning("Error", "Directory not selected.")
            return

        self.text_output.insert(tk.END, f"Started {operation_name}...\n")
        self.text_output.update_idletasks()

        try:
            result = operation_func()
            self.text_output.insert(tk.END, f"{operation_name.capitalize()} completed.\n")
            if result:
                self.text_output.insert(tk.END, f"Result: {result}\n")
        except Exception as e:
            logging.error(f"Error during {operation_name}: {e}")
            self.text_output.insert(tk.END, f"Error: {e}\n")
            messagebox.showerror("Error", f"An error occurred: {e}")

    def _find_and_delete_duplicates(self):
        """Finds and deletes duplicate files."""
        duplicates = self.processor.find_duplicate_files()
        if duplicates:
            self.text_output.insert(tk.END, "Duplicate files found:\n")
            for hash_val, paths in duplicates.items():
                self.text_output.insert(tk.END, f"Hash: {hash_val}\n")
                for path in paths:
                    self.text_output.insert(tk.END, f"  {path}\n")
            self.processor.delete_duplicates(duplicates)
            return "Duplicates deleted."
        return "No duplicates found."

    def _generate_statistics_wrapper(self):
        """Generates and displays statistics."""
        metadata_list = self.processor.analyze_directory()
        df, stats = self.processor.generate_statistics(metadata_list)
        self._display_statistics(stats)
        self.visualizer.visualize_statistics(df)
        return "Statistics generated and visualized."

    def _randomize_filenames_wrapper(self):
        """Randomizes file names."""
        return self.processor.randomize_filenames()

    def _display_statistics(self, stats):
        """Displays statistics in the text field."""
        self.text_output.insert(tk.END, "Descriptive statistics:\n")
        if 'sex_distribution' in stats and stats['sex_distribution'] is not None:
            self.text_output.insert(tk.END, "Sex distribution:\n")
            for sex, count in stats['sex_distribution'].items():
                self.text_output.insert(tk.END, f"  {sex}: {count}\n")
        if 'age_distribution' in stats and stats['age_distribution'] is not None:
            self.text_output.insert(tk.END, "\nAge distribution:\n")
            age_stats = stats['age_distribution']
            self.text_output.insert(tk.END, f"  Count: {int(age_stats['count'])}\n")
            self.text_output.insert(tk.END, f"  Mean age: {age_stats['mean']:.2f} years\n")
            self.text_output.insert(tk.END, f"  Minimum age: {age_stats['min']} years\n")
            self.text_output.insert(tk.END, f"  Maximum age: {age_stats['max']} years\n")
        if 'duration_stats' in stats and stats['duration_stats'] is not None:
            self.text_output.insert(tk.END, "\nRecording duration statistics (minutes):\n")
            duration_stats = stats['duration_stats']
            self.text_output.insert(tk.END, f"  Mean duration: {duration_stats['mean']:.2f} min\n")
            self.text_output.insert(tk.END, f"  Minimum duration: {duration_stats['min']:.2f} min\n")
            self.text_output.insert(tk.END, f"  Maximum duration: {duration_stats['max']:.2f} min\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = EDFApp(root)
    root.mainloop()