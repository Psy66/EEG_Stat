import csv

def remove_first_column(input_file, output_file):
	"""Удаляет первый столбец из CSV-файла и сохраняет результат в новый файл."""
	try:
		with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
				open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

			reader = csv.reader(infile)
			writer = csv.writer(outfile)

			for row in reader:
				# Удаляем первый столбец и записываем оставшиеся данные
				writer.writerow(row[1:])

		print(f"Результат успешно записан в файл: {output_file}")

	except FileNotFoundError:
		print(f"Ошибка: файл '{input_file}' не найден.")
	except Exception as e:
		print(f"Ошибка при обработке файла: {e}")

# Запрос имени файла у пользователя
input_csv = input("Введите имя CSV-файла для обработки: ")
output_csv = input("Введите имя выходного файла: ")

# Вызов функции для удаления первого столбца
remove_first_column(input_csv, output_csv)