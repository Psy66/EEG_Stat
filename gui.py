import os
import csv
import logging
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
        """Initialize the user interface."""
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
        """Create a tooltip for the widget."""
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
        """Show the tooltip."""
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        tooltip.wm_geometry(f"+{x}+{y}")
        tooltip.deiconify()

    def select_directory(self):
        """Select a directory containing EDF files."""
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.text_output.insert(tk.END, f"Selected directory: {self.directory}\n")
            for btn in self.button_frame.winfo_children():
                if isinstance(btn, tk.Button) and btn["text"] != "Open Folder":
                    btn.config(state=tk.NORMAL)

    def rename_files(self):
        """Rename EDF files."""
        self._execute_operation("file renaming process", rename_edf_files)

    def find_duplicates(self):
        """Find and delete duplicates."""
        self._execute_operation("duplicate search process", self._find_and_delete_duplicates)

    def check_corrupted(self):
        """Check for corrupted files."""
        self._execute_operation("corrupted file check process", find_and_delete_corrupted_edf)

    def generate_stats(self):
        """Generate statistics."""
        self._execute_operation("statistics generation process", self._generate_statistics_wrapper)

    def find_similar_time(self):
        """Find files with similar start times."""
        self._execute_operation("similar time search process", find_edf_with_similar_start_time)

    def generate_patient_table(self):
        """Generate patient table."""
        self._execute_operation("patient table creation process", self._generate_patient_table_wrapper)

    def randomize_filenames(self):
        """Randomize file names."""
        self._execute_operation("filename randomization process", self._randomize_filenames_wrapper)

    def remove_patient_info(self):
        """Remove patient information."""
        self._execute_operation("patient information removal process", self._remove_patient_info_wrapper)

    def read_edf_info(self):
        """Read EDF file information."""
        self._execute_operation("EDF file information reading process", self._read_edf_info_wrapper)

    def _execute_operation(self, operation_name, operation_func):
        """Execute an operation with error handling."""
        if not self.directory:
            messagebox.showwarning("Error", "Directory not selected.")
            return

        self.text_output.insert(tk.END, f"Started {operation_name}...\n")
        self.text_output.update_idletasks()

        try:
            result = operation_func(self.directory)
            self.text_output.insert(tk.END, f"{operation_name.capitalize()} completed.\n")
            if result:
                self.text_output.insert(tk.END, f"Result: {result}\n")
        except Exception as e:
            logging.error(f"Error during {operation_name}: {e}")
            self.text_output.insert(tk.END, f"Error: {e}\n")
            messagebox.showerror("Error", f"An error occurred: {e}")

    def _find_and_delete_duplicates(self, directory):
        """Find and delete duplicate files."""
        duplicates = find_duplicate_files(directory)
        if duplicates:
            self.text_output.insert(tk.END, "Duplicate files found:\n")
            for hash_val, paths in duplicates.items():
                self.text_output.insert(tk.END, f"Hash: {hash_val}\n")
                for path in paths:
                    self.text_output.insert(tk.END, f"  {path}\n")
            delete_duplicates(duplicates)
            return "Duplicates deleted."
        return "No duplicates found."

    def _generate_statistics_wrapper(self, directory):
        """Generate and display statistics."""
        output_directory = os.path.join(directory, "output")
        os.makedirs(output_directory, exist_ok=True)

        try:
            metadata_list = analyze_directory(directory)
            df, stats = generate_statistics(metadata_list)
            self._display_statistics(stats)
            output_csv_path = os.path.join(output_directory, 'edf_metadata_stats.csv')
            df.to_csv(output_csv_path, index=False)
            visualize_statistics(df, output_directory)
            return f"Statistics saved to {output_csv_path}"
        except Exception as e:
            logging.error(f"Error during statistics generation: {e}")
            raise

    def _generate_patient_table_wrapper(self, directory):
        """Generate patient table."""
        output_file = "patient_table.csv"
        output_directory = os.path.join(directory, "output")
        os.makedirs(output_directory, exist_ok=True)
        output_path = os.path.join(output_directory, output_file)

        try:
            files = [f for f in os.listdir(directory) if f.endswith(".edf")]
            patient_names = set()

            for file in tqdm(files, desc="Processing files", unit="file"):
                try:
                    name = self._extract_patient_name(file)
                    translated_name = translit(name, 'ru')
                    patient_names.add(translated_name)
                except Exception as e:
                    self.text_output.insert(tk.END, f"Error processing file {file}: {e}\n")

            sorted_names = sorted(patient_names)

            with open(output_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Patient Name"])
                for name in sorted_names:
                    writer.writerow([name])

            return f"Patient table saved to {output_path}"
        except Exception as e:
            logging.error(f"Error during patient table generation: {e}")
            raise

    def _randomize_filenames_wrapper(self, directory):
        """Randomize file names."""
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

        return f"File names randomized. Correspondence table saved to {output_csv_path}"

    def _remove_patient_info_wrapper(self, directory):
        """Remove patient information from EDF files."""
        files = [f for f in os.listdir(directory) if f.endswith(".edf")]
        for file in tqdm(files, desc="Processing files", unit="file"):
            try:
                self._remove_patient_info(file)
                self.text_output.insert(tk.END, f"Patient information removed from file {file}\n")
            except Exception as e:
                logging.error(f"Error removing patient information from file {file}: {e}")
                self.text_output.insert(tk.END, f"Error processing file {file}: {e}\n")

    def _read_edf_info_wrapper(self, directory):
        """Read and display information from EDF file."""
        files = [f for f in os.listdir(directory) if f.endswith(".edf")]
        for file in files:
            try:
                info = self._read_edf_info(file)
                self.text_output.insert(tk.END, f"Information from file {file}:\n{info}\n")
            except Exception as e:
                logging.error(f"Error reading information from file {file}: {e}")
                self.text_output.insert(tk.END, f"Error processing file {file}: {e}\n")

    def _generate_unique_code(self, used_codes):
        """Generate a unique 6-digit numeric code."""
        while True:
            code = ''.join(random.choices('0123456789', k=6))
            if code not in used_codes:
                used_codes.add(code)
                return code

    def _extract_patient_name(self, file):
        """Extract patient name from EDF file."""
        # Logic to extract patient name
        pass

    def _remove_patient_info(self, file):
        """Remove patient information from EDF file."""
        # Logic to remove patient information
        pass

    def _read_edf_info(self, file):
        """Read information from EDF file."""
        # Logic to read information from EDF file
        pass

    def _display_statistics(self, stats):
        """Display statistics."""
        # Logic to display statistics
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = EDFApp(root)
    root.mainloop()