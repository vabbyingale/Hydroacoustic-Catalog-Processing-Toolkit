import re
import datetime
import os

class Pick:
    def __init__(self, pick_text):
        #labels = ['isolated_t_phase', 'composite_pst_t', 'composite_pt_t', 'paired_t1', 'impulsive_I', 'II_impulsive', 'doublet', 'uncategorized']
        # Based on the signal of interest, write down the name of label from the above list (e.g. II_impulsive)
        labels = ['II_impulsive']
        if not any(label in pick_text for label in labels):
            return

        self.hydrophones = list(pick_text.rstrip().split('\n')[-1].split()[2])
        self.detection_times = []
        self.received_levels = []
        self.label = ""

        src_t = re.findall(r'([0-9]{14})', pick_text)[0]
        
        year, day, hour, minute, second, millisecond = src_t[:4].strip(), src_t[4:7].strip(), int(src_t[7:9]), int(src_t[9:11]), int(src_t[11:13]), int(src_t[13])
        
        combined = year + day
        combined_clean = re.sub(r'[^0-9]', '', combined)

        
        dt = datetime.datetime.strptime(combined_clean, '%Y%j')
        dt = dt.replace(hour=hour, minute=minute, second=second % 60, microsecond=millisecond * 10 ** 5)
        if second == 60:
            dt -= datetime.timedelta(minutes=1)

        self.est_source_time = dt

        self.est_source_level = re.findall(r'(\d{1,3}\.\d{2})\s', pick_text)[-1]
        est_source_lat = float(re.findall(r'([-]{0,1}\d{1,3}\.\d{3,4})\s', pick_text)[0])
        est_source_lon = float(re.findall(r'([-]{0,1}\d{1,3}\.\d{3,4})\s', pick_text)[1])
        
        self.est_source_pos = [est_source_lat, est_source_lon]

        for hydrophone in self.hydrophones:
            pos = self.hydrophones.index(hydrophone)
            right_pick = re.findall(r'((\d{4})\s*([\d\s]{9}\.[0-9]{3})).*\n', pick_text)[pos]

            year, date = right_pick[1].strip(), right_pick[2].strip()
            date = date.replace(' ', '0')

            year, day, hour, minute, second, millisecond = year, \
                date[:3], int(date[3:5]), int(date[5:7]), int(date[7:9]), int(date[10:])

            dt = datetime.datetime.strptime(year + day, '%Y%j')
            dt = dt.replace(hour=hour, minute=minute, second=second, microsecond=millisecond * 10 ** 3)
            self.detection_times.append(dt)
            self.received_levels.append(float(re.findall(r'(\d{1,3}\.\d{2})\s', pick_text)[pos]))

    def __lt__(self, other):
        return self.est_source_time < other.est_source_time


class PickFile:
    def __init__(self, path):
        self.path = path

        with open(path, 'rb') as file:
            data = file.read().decode('ascii')
        self._process_data(data)

    def _process_data(self, data):
        picks = re.split(r'\n\s*\d{1,2}\s*\n', data, flags=re.MULTILINE)

        self.picks = []
        for pick_text in picks:
            if len(pick_text) == 0:
                continue
            pick = Pick(pick_text)
            if hasattr(pick, 'est_source_time'):  # Check if the Pick object was fully initialized
                self.picks.append(pick)

        self.picks.sort()

    def __getitem__(self, item):
        for pick in self.picks:
            if pick.est_source_time == item:
                return pick

    def getSingleHydro(self, hydrophone):
        res = []
        for pick in self.picks:
            if hydrophone in pick.hydrophones:
                idx = pick.hydrophones.index(hydrophone)
                res.append((pick.est_source_time, pick.detection_times[idx], pick.label, pick.received_levels[idx]))
        return res

    def toCsv(self, output_dir, input=None, hydrophones=None, offset=datetime.timedelta(seconds=0)):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
        for pick in self.picks:
            res = "station,class,start_date,end_date,received_level"
            for hi in range(len(pick.hydrophones)):
                time = pick.detection_times[hi] + offset
                formatted_time = time.strftime("%Y,%m,%d,%H,%M,%S") + f",{int(time.microsecond / 1000):03d}"
                h = pick.hydrophones[hi]
                received_level = pick.received_levels[hi]
                if input is not None:
                    h = input.hydrophone_names[list(input.hydrophone_letters).index(h)]
                if (hydrophones is not None and h in hydrophones) or hydrophones is None:
                    res += f"\n{h},doublet,{formatted_time},{received_level}"  # <-- label used here

            filename = pick.est_source_time.strftime("%Y%m%d_%H%M%S_D_RL") + ".csv"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w") as f:
                f.write(res)

class PickFile_association:
    def __init__(self, path):
        self.path = path

        with open(path, 'rb') as file:
            data = file.read().decode('ascii')
        self._process_data(data)

    def _process_data(self, data):
        picks = re.split(r'\n\s*\d{1,2}\s*\n', data, flags=re.MULTILINE)

        self.picks = []
        for pick_text in picks:
            if len(pick_text) == 0:
                continue
            pick = Pick(pick_text)
            if hasattr(pick, 'est_source_time'):  # Check if the Pick object was fully initialized
                self.picks.append(pick)

        self.picks.sort()

    def __getitem__(self, item):
        for pick in self.picks:
            if pick.est_source_time == item:
                return pick

    def getSingleHydro(self, hydrophone):
        res = []
        for pick in self.picks:
            if hydrophone in pick.hydrophones:
                idx = pick.hydrophones.index(hydrophone)
                res.append((pick.est_source_time, pick.detection_times[idx], pick.label, pick.received_levels[idx]))
        return res

    def toCsv(self, output_dir, input=None, hydrophones=None, offset=datetime.timedelta(seconds=0)):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for pick in self.picks:
            res = "station,class,year,month,date,hour,minute,second,ms,RL"
            for hi in range(len(pick.hydrophones)):
                time = pick.detection_times[hi] + offset
                formatted_time = time.strftime("%Y,%m,%d,%H,%M,%S") + f",{int(time.microsecond / 1000):03d}"
                h = pick.hydrophones[hi]
                received_level = pick.received_levels[hi]  # Fetch the received level
                if input is not None:
                    h = input.hydrophone_names[list(input.hydrophone_letters).index(h)]
                if (hydrophones is not None and h in hydrophones) or hydrophones is None:
                    res += f"\n{h},doublet,{formatted_time},{received_level}"

            filename = pick.est_source_time.strftime("%Y%m%d_%H%M%S_RL") + ".csv"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w") as f:
                f.write(res)
