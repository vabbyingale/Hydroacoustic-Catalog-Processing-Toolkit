#!/usr/bin/env python3
"""
Extract time and received level data per hydrophone for each event.

This script reads a .pick file containing arrival picks and a .input file
defining hydrophone mappings. It then extracts:
- Time in year, month, date, hour, minute, second, and millisecond format
- Received level (in dB) for each hydrophone

The selected hydrophones are defined in the script.
Output is saved to a CSV file in the specified output directory.
"""

import logging
from InputLoader import InputFile
from PickLoader_Received_Level import PickFile_association

def main():
    # Set paths and hydrophone list
    output_path = "./Impulsive_II"  # Output directory (this will depend on the label is given in PickLoader_Received_Level.py)
    hydrophones = ["H32", "H38", "H40", "H41"]  # Desired hydrophones
    pick_file_path = "Aleutian_Hydroacoustic_catalog.pick"  # Input .pick file
    station_input_path = "Aleutian_Station.input"  # Input .input file

    try:
        picks = PickFile_association(pick_file_path)
        input_data = InputFile(station_input_path)

        picks.toCsv(output_path, input_data, hydrophones)

        logging.info("Extraction complete. Results are saved.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
