# edf_rnd_name.py
import os
import random
import csv

# Функция для генерации уникального 6-значного цифрового кода
def generate_unique_code(used_codes):
	while True:
		code = ''.join(random.choices('0123456789', k=6))
		if code not in used_codes:
			used_codes.add(code)
			return code

# Запрашиваем путь к директории у пользователя
directory = input("Введите путь к директории с файлами: ")

# Переходим в указанную директорию
os.chdir(directory)

# Получаем список файлов в указанной директории
files = [f for f in os.listdir() if os.path.isfile(f)]

# Создаем множество для хранения уже использованных кодов
used_codes = set()

# Создаем список для хранения соответствия старых и новых имен
name_mapping = []

# Переименовываем файлы
for old_name in files:
	# Генерируем уникальный код
	new_name = generate_unique_code(used_codes) + os.path.splitext(old_name)[1]

	# Переименовываем файл
	os.rename(old_name, new_name)

	# Добавляем соответствие в список
	name_mapping.append((old_name, new_name))

# Сохраняем соответствие в CSV-файл
with open('name_mapping.csv', 'w', newline='', encoding='utf-8') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(['Old Name', 'New Name'])
	writer.writerows(name_mapping)

print(f"Файлы успешно переименованы в директории {directory}.")
print("Таблица соответствия сохранена в name_mapping.csv.")