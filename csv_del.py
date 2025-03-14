# csv_del.py
import csv

def remove_first_column(input_file, output_file):
    """Removes the first column from a CSV file and saves the result to a new file."""
    try:
        with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
                open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row in reader:
                # Remove the first column and write the remaining data
                writer.writerow(row[1:])

        print(f"Result successfully written to file: {output_file}")

    except FileNotFoundError:
        print(f"Error: file '{input_file}' not found.")
    except Exception as e:
        print(f"Error processing the file: {e}")

# Prompt the user for the file name
input_csv = input("Enter the name of the CSV file to process: ")
output_csv = input("Enter the name of the output file: ")

# Call the function to remove the first column
remove_first_column(input_csv, output_csv)