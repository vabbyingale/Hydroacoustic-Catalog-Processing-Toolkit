# Hydroacoustic Catalog Processing Toolkit

This open-source toolkit provides a pipeline for processing hydroacoustic event data recorded by underwater hydrophones. It includes tools to extract event arrival times and received levels, convert time data to seconds, estimate signal source bearings, and visualize bearing distributions.

---

## Features

**Time and Received Level Extraction**: Parses `.pick` and `.input` files to extract detailed arrival times and received levels (in dB) for selected hydrophones.
**Arrival Time Conversion**: Converts timestamp data to total seconds for simplified numerical analysis.
**Bearing Estimation and Visualization**: Calculates the bearing (direction) of the acoustic source using triangulation and visualizes the results with a polar plot.
**Custom Color Mapping**: Visualizes bearing distributions using a density-based purple-to-black colormap.

---

## Repository Structure

```
.
├── extract_time_per_hydrophone.py     			  # Step 1: Extract time and received level from pick files
├── time_conversion.py                            # Step 2: Convert timestamps to seconds
├── bearing_analysis.py                           # Step 3: Estimate bearings and visualize data
├── InputLoader.py                                # Helper module to load station metadata
├── PickLoader_Received_Level.py                  # Helper module to parse pick files
├── Aleutian_Hydroacoustic_catalog.pick           # Example pick file (arrival data)
├── Aleutian_station.input                        # Example input file (station metadata)
└── README.md
```

---

## Installation

This toolkit requires Python 3 and the following packages:

```bash
pip install numpy pandas matplotlib scipy
```

---

## Usage

### 🔹 Step 1: Extract Time and Received Levels

```bash
python extract_time_per_hydrophone.py
```

* **Inputs**:

  * `Zenodo_ALU_catalog.pick`: Arrival pick file
  * `Zenodo_ALU_station.input`: Hydrophone station metadata
  
* **Requirements**:

  * Make folders with given label names for future references
* **Outputs**:

  * Per-event CSV files containing arrival time components and received level in given directiory (e.g. `./Impulsive_II/`)

Customize:

* The hydrophones of interest are defined in the `hydrophones` list in the script (default: `["H32", "H38", "H40", "H41"]`).
* The output directory can be modified in the `output_path` variable.

---

### 🔹 Step 2: Convert Arrival Time to Seconds

```bash
python time_conversion.py
```

* **Input**: All CSV files from given (e.g.`./Impulsive_II/`) directory
* **Output**: Simplified CSV files with `station`, `class`, and `time_seconds` columns, saved in another directory (e.g.`./Impulsive_II/converted_imp_II/`)

Each file is transformed to ease numerical analysis and comparison of arrival times between stations.

---

### 🔹 Step 3: Estimate Signal Bearings and Plot

```bash
python bearing_analysis.py
```

* **Input**: All converted files from given folder (e.g.`./Impulsive_II/converted_imp_II/`)

* **Output**: Polar plot showing the bearing of each event with color intensity indicating event density

The bearings are calculated using time-difference-of-arrival (TDOA) triangulation based on hydrophone positions.

---

## Customization

* **Station Coordinates**: Update `STATION_COORDINATES` in `bearing_analysis.py` to reflect your hydrophone array.
* **Signal Speed**: Modify the constant `SIGNAL_SPEED` (default = 1462 m/s) to match your environment.
* **Filename Convention**: The regex in `extract_datetime_from_filename()` assumes filenames follow `YYYYMMDD_HHMMSS` format.

---

## Logging and Error Handling

All scripts implement informative logging. Errors and progress updates are printed to the terminal.

---

## Example Workflow

```bash
# Step 1
python extract_time_per_hydrophone.py

# Step 2
python time_conversion.py

# Step 3
python bearing_analysis.py
```