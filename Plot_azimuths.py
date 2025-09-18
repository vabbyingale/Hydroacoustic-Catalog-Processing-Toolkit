import os
import csv
import re
import logging
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.ticker import MaxNLocator


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Constants
SIGNAL_SPEED = 1462  # Speed of acoustic signal in m/s
STATION_COORDINATES = {
    "H32": np.array([53.3396, -176.5764]),
    "H41": np.array([53.2725, -176.4712]),
    "H40": np.array([53.3384, -176.3639]),
    "H38": np.array([53.4038, -176.4708])
}

# Given a folder name that has been generated from time_conversion.py code (e.g. Impulsive_II/converted_imp_II)
INPUT_DIRECTORY = 'Impulsive_II/converted_imp_II/'

def calculate_bearing(arrival_times, stations=STATION_COORDINATES, v=SIGNAL_SPEED):
    """
    Estimate the bearing of a signal source based on arrival times at different stations.
    """
    available_stations = list(arrival_times.keys())
    t = {s: arrival_times[s] for s in available_stations}

    delta_t = {
        f"{s1}_{s2}": t[s1] - t[s2]
        for i, s1 in enumerate(available_stations)
        for s2 in available_stations[i + 1:]
    }

    delta_d = {k: v * dt for k, dt in delta_t.items()}

    def objective(xy):
        x, y = xy
        return sum(
            ((np.linalg.norm(np.array([x, y]) - stations[s1]) -
              np.linalg.norm(np.array([x, y]) - stations[s2]) - delta_d[f"{s1}_{s2}"])**2)
            for i, s1 in enumerate(available_stations)
            for s2 in available_stations[i + 1:]
        )

    initial_guess = np.mean([stations[s] for s in available_stations], axis=0)
    result = minimize(objective, initial_guess)
    source_loc = result.x

    ref_station = "H38" if "H38" in available_stations else available_stations[0]
    dx = source_loc[0] - stations[ref_station][0]
    dy = source_loc[1] - stations[ref_station][1]

    bearing_rad = np.arctan2(dy, dx)
    bearing_deg = np.degrees(bearing_rad) % 360

    return bearing_deg


def parse_csv_file(filepath):
    """
    Parse CSV file and extract arrival times.
    """
    arrival_times = {}
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                station = row[0].strip()
                arrival_time = float(row[2])
                arrival_times[station] = arrival_time
            except (IndexError, ValueError):
                continue
    return arrival_times


def extract_datetime_from_filename(filename):
    """
    Extract datetime string from filename using regex.
    """
    match = re.search(r'(\d{8})_(\d{6})', filename)
    if match:
        date_str, time_str = match.groups()
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
    return "Unknown"


def load_data(directory):
    """
    Load all arrival time data from CSV files and compute bearings.
    """
    data = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            filepath = os.path.join(directory, filename)
            try:
                arrival_times = parse_csv_file(filepath)
                bearing = calculate_bearing(arrival_times)
                timestamp = extract_datetime_from_filename(filename)
                data.append((filename, timestamp, bearing))
            except Exception as e:
                logging.warning(f"Skipping {filename}: {e}")
    return data


def create_colormap():
    """
    Create a custom purple-to-black colormap.
    """
    start_color = (123/255, 50/255, 148/255)
    black = (0, 0, 0)
    colors_list = [
        (0.0, start_color),
        (0.1, (120/255, 50/255, 147/255)),
        (0.2, (115/255, 55/255, 145/255)),
        (0.3, (105/255, 52/255, 140/255)),
        (0.4, (90/255, 45/255, 135/255)),
        (0.5, (75/255, 37/255, 125/255)),
        (0.6, (60/255, 30/255, 100/255)),
        (0.7, (45/255, 22/255, 75/255)),
        (0.8, (30/255, 15/255, 50/255)),
        (0.9, (15/255, 7/255, 25/255)),
        (1.0, black)
    ]
    return LinearSegmentedColormap.from_list('purple_to_black', colors_list)


def plot_bearings(data):
    """
    Plot bearings on a polar plot with density-based coloring.
    """
    bearings_deg = np.array([bearing for _, dt, bearing in data if dt != "Unknown"])
    bearings_rad = np.radians(bearings_deg)

    bins = np.arange(0, 361, 10)
    bin_counts, _ = np.histogram(bearings_deg, bins=bins)
    norm = Normalize(vmin=0, vmax=bin_counts.max())

    bin_indices = np.digitize(bearings_deg, bins) - 1
    colors = bin_counts[bin_indices]

    cmap = create_colormap()

    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    for bearing, color_val in zip(bearings_rad, colors):
        ax.plot([bearing, bearing], [0, 1], color=cmap(norm(color_val)), lw=1)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_clim(0, np.max(bin_counts))

    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.1)
    cbar.set_label('Number of Events', fontsize=14)
    cbar.set_ticks(MaxNLocator(integer=True).tick_values(0, np.max(bin_counts)))
    cbar.ax.tick_params(labelsize=12)

    ax.set_yticklabels([])
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    plt.tight_layout()
    plt.show()


def main():
    """
    Main execution function.
    """
    logging.info("Loading data...")
    data = load_data(INPUT_DIRECTORY)
    logging.info(f"Loaded {len(data)} events.")
    plot_bearings(data)


if __name__ == "__main__":
    main()
