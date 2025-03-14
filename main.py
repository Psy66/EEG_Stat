# main.py
import os

from edf_reader import analyze_directory
from eeg_statistics import generate_statistics, visualize_statistics
from utils import check_directory

def main():
    """Main function for analyzing and visualizing data."""
    input_directory = input("Enter the path to the folder containing EDF files: ").strip()
    output_directory = os.path.join(input_directory, "output")

    try:
        check_directory(input_directory)
        os.makedirs(output_directory, exist_ok=True)

        metadata_list = analyze_directory(input_directory)
        df, stats = generate_statistics(metadata_list)

        print("Descriptive statistics:")
        print(stats)

        output_csv_path = os.path.join(output_directory, 'edf_metadata_stats.csv')
        df.to_csv(output_csv_path, index=False)
        print(f"Statistics saved to {output_csv_path}")

        visualize_statistics(df, output_directory)
        print(f"Graphs saved to {output_directory}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()