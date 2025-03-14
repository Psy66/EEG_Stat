# 🧠 EDF File Manager

![EDF File Manager](https://img.shields.io/badge/Version-1.0.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)

**EDF File Manager** is a user-friendly application with a graphical interface for managing files in the EDF (European Data Format). The program provides powerful tools for working with EDF files, including renaming, checking for corruption, finding duplicates, generating statistics, and more.

---

## ✨ Features

- **📂 Open Folder with EDF Files**: Select a directory to work with files.
- **🖋️ Rename EDF Files**: Automatically rename files based on metadata.
- **🚫 Remove Corrupted Files**: Find and delete corrupted EDF files.
- **🔍 Remove Duplicates**: Find and delete duplicate EDF files.
- **⏱️ Find Files with Similar Start Time**: Locate EDF files with similar recording start times.
- **📊 Generate Statistics**: Collect and visualize statistics for EDF files.
- **📋 Create Patient Table**: Generate a CSV table with patient names.
- **🎲 Randomize Filenames**: Randomize filenames in the folder.
- **👤 Remove Patient Info**: Remove patient information from EDF files.
- **📄 Read EDF File Info**: Display information about the selected EDF file.

---

## 🛠️ Installation

1. Ensure you have **Python 3.8** or higher installed.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python gui.py
   ```

---

## 🖥️ Usage

1. Launch the application.
2. Select a folder with EDF files using the **"Open Folder"** button.
3. Use the corresponding buttons to perform the desired operations:
   - **🖋️ Rename EDF**: Renames files based on metadata.
   - **🚫 Remove Corrupted**: Deletes corrupted files.
   - **🔍 Remove Duplicates**: Deletes duplicate files.
   - **⏱️ Find Similar**: Finds files with similar recording start times.
   - **📊 Generate Statistics**: Generates statistics for the files.
   - **📋 Create Patient Table**: Creates a CSV table with patient names.
   - **🎲 Randomize Filenames**: Randomizes filenames.
   - **👤 Remove Patient Info**: Removes patient information from files.
   - **📄 Read EDF Info**: Displays information about the selected EDF file.

---

## 📦 Dependencies

- `tkinter`: For creating the graphical interface.
- `mne`: For working with EDF files.
- `pandas`: For data processing and generating statistics.
- `tqdm`: For displaying progress during operations.
- `transliterate`: For transliterating patient names.

---

## 📜 License

This project is licensed under the **MIT License**. For details, see the [LICENSE](LICENSE) file.

---

## 👨‍💻 Author

**Tim Liner**  
📧 Email: [psy66@narod.ru](mailto:psy66@narod.ru)

---

## ❓ Support

If you have any questions or suggestions, please contact me at [psy66@narod.ru](mailto:psy66@narod.ru).  
Your feedback and ideas will help make this project better! 🚀

---

# 🧠 EDF File Manager

**EDF File Manager** — это удобное приложение с графическим интерфейсом для управления файлами в формате EDF (European Data Format). Программа предоставляет мощные инструменты для работы с EDF-файлами, включая переименование, проверку на повреждения, поиск дубликатов, генерацию статистики и многое другое.

---

## ✨ Возможности

- **📂 Открытие папки с EDF-файлами**: Выбор директории для работы с файлами.
- **🖋️ Переименование EDF-файлов**: Автоматическое переименование на основе метаданных.
- **🚫 Удаление поврежденных файлов**: Поиск и удаление поврежденных EDF-файлов.
- **🔍 Удаление дубликатов**: Поиск и удаление дубликатов EDF-файлов.
- **⏱️ Поиск файлов с близким временем начала**: Нахождение EDF-файлов с похожим временем начала записи.
- **📊 Генерация статистики**: Сбор и визуализация статистики по EDF-файлам.
- **📋 Создание таблицы пациентов**: Генерация CSV-таблицы с именами пациентов.
- **🎲 Рандомизация имен файлов**: Рандомизация имен файлов в папке.
- **👤 Удаление информации о пациенте**: Удаление информации о пациенте из EDF-файлов.
- **📄 Чтение информации из EDF-файла**: Отображение информации о выбранном EDF-файле.

---

## 🛠️ Установка

1. Убедитесь, что у вас установлен **Python 3.8** или выше.
2. Установите необходимые зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Запустите приложение:

   ```bash
   python gui.py
   ```

---

## 🖥️ Использование

1. Запустите приложение.
2. Выберите папку с EDF-файлами с помощью кнопки **"Открыть папку"**.
3. Используйте соответствующие кнопки для выполнения нужных операций:
   - **🖋️ Переименовать EDF**: Переименует файлы на основе метаданных.
   - **🚫 Удалить поврежденные**: Удаляет поврежденные файлы.
   - **🔍 Удалить дубликаты**: Удаляет дубликаты файлов.
   - **⏱️ Найти похожие**: Находит файлы с близким временем начала записи.
   - **📊 Сгенерировать статистику**: Генерирует статистику по файлам.
   - **📋 Создать таблицу пациентов**: Создает CSV-таблицу с именами пациентов.
   - **🎲 Рандомизировать названия**: Рандомизирует имена файлов.
   - **👤 Удалить patientinfo**: Удаляет информацию о пациенте из файлов.
   - **📄 Прочитать info EDF**: Отображает информацию о выбранном EDF-файле.

---

## 📦 Зависимости

- `tkinter`: Для создания графического интерфейса.
- `mne`: Для работы с EDF-файлами.
- `pandas`: Для обработки данных и генерации статистики.
- `tqdm`: Для отображения прогресса выполнения операций.
- `transliterate`: Для транслитерации имен пациентов.

---

## 📜 Лицензия

Этот проект распространяется под лицензией **MIT**. Подробности см. в файле [LICENSE](LICENSE).

---

## 👨‍💻 Автор

**Tim Liner**  
📧 Email: [psy66@narod.ru](mailto:psy66@narod.ru)

---

## ❓ Поддержка

Если у вас возникли вопросы или предложения, пожалуйста, свяжитесь со мной по адресу [psy66@narod.ru](mailto:psy66@narod.ru).  
Ваши отзывы и идеи помогут сделать этот проект лучше! 🚀
```
