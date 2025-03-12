# edfinfo_chg.py
import os

def replace_patient_name_in_edf(edf_file_path):
	# Открываем файл в режиме чтения и записи (бинарный режим)
	with open(edf_file_path, 'r+b') as f:
		f.seek(8)  # Переходим к началу поля patientname (8-й байт)
		patientname = f.read(80).decode('ascii')  # Читаем текущее поле patientname

		# Разделяем поле patientname на части
		parts = patientname.split(' ', 3)  # Разделяем по пробелам, но не более 3 раз
		if len(parts) >= 3:
			# Сохраняем первые три части (UUID, пол, дата рождения)
			new_patientname = ' '.join(parts[:3])
			# Заменяем имя пациента на символы '_' той же длины
			name_to_replace = parts[3].split('Startdate')[0]  # Убираем "Startdate" и всё после
			new_patientname += ' ' + ('_' * len(name_to_replace))  # Заменяем имя на '_'
			# Добавляем оставшуюся часть (если есть)
			if 'Startdate' in parts[3]:
				new_patientname += ' ' + parts[3].split('Startdate', 1)[1]
			# Дополняем до 80 символов
			new_patientname = new_patientname.ljust(80)
		else:
			# Если структура не соответствует ожидаемой, оставляем поле как есть
			new_patientname = patientname

		# Записываем новое поле patientname
		f.seek(8)
		f.write(new_patientname.encode('ascii'))

input_directory = input("Введите путь к директории с EDF-файлами: ")

if not os.path.isdir(input_directory):
	print("Указанная директория не существует.")
else:
	edf_files = [f for f in os.listdir(input_directory) if f.endswith('.edf')]
	if not edf_files:
		print("В директории нет EDF-файлов.")
	else:
		for file_name in edf_files:
			edf_file_path = os.path.join(input_directory, file_name)
			try:
				replace_patient_name_in_edf(edf_file_path)
				print(f"Файл {file_name} обработан.")
			except Exception as e:
				print(f"Ошибка при обработке файла {file_name}: {e}")

		# Проверяем последний файл
		last_file = edf_files[-1]
		edf_file_path = os.path.join(input_directory, last_file)
		with open(edf_file_path, 'rb') as f:
			f.seek(8)
			patientname = f.read(80).decode('ascii').strip()
			print(f"\nИнформация о последнем обработанном файле ({last_file}):")
			print(f"Имя пациента: {patientname}")