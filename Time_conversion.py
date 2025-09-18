#!/usr/bin/env python3
"""
Convert arrival time data in CSV files to seconds and save simplified output.

This script processes all CSV files in a predefined input folder. It computes
the arrival time in seconds for each row and saves the result to a new CSV file
with only the 'station', 'class', and computed 'time_seconds' columns.
"""

import os
import glob
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Given a folder name that has been generated from extract_time_per_hydrophone.py code (e.g. Impulsive_II)
INPUT_FOLDER = "./Impulsive_II"

def convert_file(file_path, output_folder):
    """
    Convert a CSV file to include time in seconds and save a simplified version.

    Parameters:
        file_path (str): Path to the input CSV file.
        output_folder (str): Directory where the output file will be saved.
    """
    try:
        df = pd.read_csv(file_path)

        # Check if required columns exist
        required_cols = {'hour', 'minute', 'second', 'ms', 'station', 'class'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing required columns: {missing}")

        # Compute time in seconds
        df['time_seconds'] = (
            df['hour'] * 3600 +
            df['minute'] * 60 +
            df['second'] +
            df['ms'] / 1000
        )

        # Keep required columns
        result = df[['station', 'class', 'time_seconds']]

        # Prepare output path
        file_name = os.path.basename(file_path)
        output_path = os.path.join(output_folder, f"{file_name.replace('.csv', '')}_seconds.csv")

        # Save without header and index
        result.to_csv(output_path, index=False, header=False)
        logging.info(f"Processed: {file_name}")

    except Exception as e:
        logging.error(f"Failed to process {file_path}: {e}")


def process_folder(input_folder):
    """
    Process all CSV files in a folder.

    Parameters:
        input_folder (str): Folder containing input CSV files.
    """
    output_folder = os.path.join(input_folder, "converted_imp_II")
    os.makedirs(output_folder, exist_ok=True)

    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    if not csv_files:
        logging.warning("No CSV files found in the input folder.")
        return

    for file_path in csv_files:
        convert_file(file_path, output_folder)


if __name__ == "__main__":
    process_folder(INPUT_FOLDER)
