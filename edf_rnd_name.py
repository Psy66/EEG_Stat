# edf_rnd_name.py
import os
import random
import csv

# Function to generate a unique 6-digit numeric code
def generate_unique_code(used_codes):
    while True:
        code = ''.join(random.choices('0123456789', k=6))
        if code not in used_codes:
            used_codes.add(code)
            return code

# Prompt the user for the directory path
directory = input("Enter the path to the directory containing the files: ")

# Change to the specified directory
os.chdir(directory)

# Get a list of files in the specified directory
files = [f for f in os.listdir() if os.path.isfile(f)]

# Create a set to store used codes
used_codes = set()

# Create a list to store the old and new name correspondence
name_mapping = []

# Rename the files
for old_name in files:
    # Generate a unique code
    new_name = generate_unique_code(used_codes) + os.path.splitext(old_name)[1]

    # Rename the file
    os.rename(old_name, new_name)

    # Add the correspondence to the list
    name_mapping.append((old_name, new_name))

# Save the correspondence in a CSV file
with open('name_mapping.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Old Name', 'New Name'])
    writer.writerows(name_mapping)

print(f"Files successfully renamed in directory {directory}.")
print("The name correspondence table is saved in name_mapping.csv.")