from datetime import datetime
from uttils import as_dict, month_to_int


class HFRadarMapper(object):
    """Mapper for old type of data from hf.met.no"""

    time_coverage = None
    geolocation = None
    col_names = []
    data = []
    metadata = {
        'general': {},
        'time': {},
        'geolocation': {},
        'transmit': {},
        'pattern': {},
        'radial': {},
        'bragg': {},
        'other': {}
    }

    def __init__(self, uri):
        self.uri = uri
        self.mapper()

    def mapper(self):

        with open(self.uri, 'r') as data_file:
            row_number = 0
            for line in data_file:
                if row_number < 3:
                    if row_number == 1:
                        self.col_names = line.strip().split('!')[-1].split(': ')[-1]
                    elif row_number == 2:
                        meta = line.strip().split()

                        year = int(meta[5])
                        month = month_to_int(meta[3])
                        day = int(meta[4][0])
                        hour, mnt, sec = [int(x) for x in meta[0].split(':')]
                        date_time = datetime(year, month, day, hour, mnt, sec)
                        self.metadata['time']['stamp'] = as_dict(value=date_time)
                        self.metadata['time']['zone'] = as_dict(value=meta[1])
                        # TODO: parse geolocation info
                    row_number += 1

                else:

                    self.data.append([float(el) for el in line.split()])

    def get_time_coverage(self):
        """Time coverage of data file from metadata"""
        time_start = time_end = self.metadata['time']['stamp']['value']
        self.time_coverage = (time_start, time_end)

    def get_geolocation(self):
        """Geolocation in format tuple()"""
        lon_min = min(self.data[9])
        lon_max = max(self.data[9])

        lat_min = min(self.data[8])
        lat_max = max(self.data[8])

        self.geolocation = ((lon_min, lon_max),
                            (lat_min, lat_max))
