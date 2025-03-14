# 🧠 EDF File Manager

![EDF File Manager](https://img.shields.io/badge/Version-1.0.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)

*EDF File Manager is a user-friendly application with a graphical interface for managing files in the EDF (European Data Format). The program provides powerful tools for working with EDF files, including renaming, checking for corruption, finding duplicates, generating statistics, and more.*

## ✨ Features

- 📂 **Open Folder with EDF Files**: Select a directory to work with files.
- 🖋️ **Rename EDF Files**: Automatically rename files based on metadata.
- 🚫 **Remove Corrupted Files**: Find and delete corrupted EDF files.
- 🔍 **Remove Duplicates**: Find and delete duplicate EDF files.
- ⏱️ **Find Files with Similar Start Time**: Locate EDF files with similar recording start times.
- 📊 **Generate Statistics**: Collect and visualize statistics for EDF files.
- 📋 **Create Patient Table**: Generate a CSV table with patient names.
- 🎲 **Randomize Filenames**: Randomize filenames in the folder.
- 👤 **Remove Patient Info**: Remove patient information from EDF files.
- 📄 **Read EDF File Info**: Display information about the selected EDF file.

## 🛠️ Installation

Ensure you have Python 3.8 or higher installed.

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python gui.py
```

## 🖥️ Usage

1. Launch the application.
2. Select a folder with EDF files using the "Open Folder" button.
3. Use the corresponding buttons to perform the desired operations:
   - 🖋️ **Rename EDF**: Renames files based on metadata.
   - 🚫 **Remove Corrupted**: Deletes corrupted files.
   - 🔍 **Remove Duplicates**: Deletes duplicate files.
   - ⏱️ **Find Similar**: Finds files with similar recording start times.
   - 📊 **Generate Statistics**: Generates statistics for the files.
   - 📋 **Create Patient Table**: Creates a CSV table with patient names.
   - 🎲 **Randomize Filenames**: Randomizes filenames.
   - 👤 **Remove Patient Info**: Removes patient information from files.
   - 📄 **Read EDF Info**: Displays information about the selected EDF file.

## 📜 License

This project is licensed under the MIT License. For details, see the LICENSE file.

## 👨‍💻 Author

Timur Petrenko  
📧 Email: psy66@narod.ru

---

## 📚 Citation

If you use this tool in your research, please consider citing it as follows:

```
Petrenko, Timur. EDF File Manager. 2025. Available on GitHub: https://github.com/Psy66/EEG_Stat.
```

---

### 📢 Important Note

This application is intended for educational and research purposes only. Use it at your own risk. The author does not take any responsibility for potential issues or damages caused by the use of this software.
