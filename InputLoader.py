import re
import numpy as np


class InputFile:
    # path: path of the .pick file which we will look for
    def __init__(self, path):
        self.path = path

        with open(path, 'rb') as file:
            data = file.read().decode('ascii')
        self._process_data(data)

    def _process_data(self, data):
        self.hydrophone_names = re.findall('\n\s*([A-Z0-9]+)\s*\n', data)

        self.hydrophone_coords = []
        coord = re.findall(r'\s*((-?\d+\.\d+\s*){' + str(len(self.hydrophone_names)) + r'})\s*\n', data)
        lats = coord[0][0].split()
        longs = coord[1][0].split()
        for i in range(len(self.hydrophone_names)):
            lat = float(lats[i])
            long = float(longs[i])
            depth = -1
            self.hydrophone_coords.append([lat, long, depth])

        self.hydrophone_letters = re.findall('[\s,]([A-Za-z0-9]+)[^\.A-Za-z0-9]', str(list(data.rstrip().split('\n'))[-6:-2]))

        idx_sort = np.argsort(np.array(self.hydrophone_letters, dtype=str))
        self.hydrophone_names = np.array(self.hydrophone_names)[idx_sort]
        self.hydrophone_coords = np.array(self.hydrophone_coords)[idx_sort]
        self.hydrophone_letters = np.array(self.hydrophone_letters)[idx_sort]
