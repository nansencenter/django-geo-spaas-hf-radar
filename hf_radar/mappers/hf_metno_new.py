from datetime import datetime, timedelta
from uttils import as_dict
import numpy as np
from hf_radar.toolbox.utils import EmptyFile


class HFRadarMapper(object):
    """Mapper for new type of data from hf.met.no"""

    time_coverage = None
    geolocation = None

    def __init__(self, uri):
        self.uri = uri
        self.col_names, self.data, self.metadata = self.mapper()
        self.data = np.array(self.data)
        self.get_time_coverage()
        self.get_geolocation()

    def mapper(self):

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

        # Dict for accumulation of additional metadata from the input file
        # The metadata will be used for validation of data mapping
        tmp = {}

        # There are several tables in a rvl file. We need only first.
        # We also need to get an information about col names only for first table
        # The <tab_flag> is used for excepting of data overwriting in similar fields
        tab_flag = True

        with open(self.uri, 'r') as data_file:
            for line in data_file:
                line = line.strip()

                # According to the file structure, the first symbol in all lines with metadata is <%>
                # Thus if condition is True - we got a line with metadata => we parse it
                if line[0] is '%':

                    # Patter for metadata row is <tag>:<values>
                    try:
                        tag, value = [el.strip() for el in line.replace('%', '').split(': ')]
                    # If we have got a row without <values> then return only tag
                    except ValueError:
                        tag = line.replace('%', '')

                    # General metadata parsing
                    if tag == 'FileType':
                        metadata['general']['type'] = as_dict(value=value, f_field=tag)
                    elif tag == 'UUID':
                        metadata['general']['id'] = as_dict(value=value, f_field=tag)
                    elif tag == 'Manufacturer':
                        metadata['general']['manufacture'] = as_dict(value=value, f_field=tag)
                    elif tag == 'Site':
                        metadata['general']['site'] = as_dict(value=value.split()[0], f_field=tag)

                    # Time metadata
                    elif tag == 'TimeStamp':
                        t_arr = value.split()
                        date_time = datetime(*[int(x) for x in t_arr])
                        metadata['time']['stamp'] = as_dict(value=date_time, f_field=tag)
                    elif tag == 'TimeZone':
                        metadata['time']['zone'] = as_dict(value=value, f_field=tag)
                    elif tag == 'TimeCoverage':
                        metadata['time']['coverage'] = as_dict(value=float(value.split()[0]),
                                                                    unit='m', f_field=tag)
                    # Geolocation metadata
                    elif tag == 'Origin':
                        value = [float(el.strip()) for el in value.split()]
                        metadata['geolocation']['origin'] = as_dict(value=value, unit='m', f_field=tag)
                    elif tag == 'GreatCircle':
                        metadata['geolocation']['great circle'] = as_dict(value=value.split(), unit='m',
                                                                               f_field=tag)
                    elif tag == 'GeodVersion':
                        metadata['geolocation']['geod version'] = as_dict(value=value.split(), unit='m',
                                                                             f_field=tag)

                    # Transmit metadata
                    elif tag == 'TransmitCenterFreqMHz':
                        metadata['transmit']['center_freq'] = as_dict(value=float(value), unit='MHz', f_field=tag)
                    elif tag == 'TransmitBandwidthKHz':
                        metadata['transmit']['band_width'] = as_dict(value=float(value), unit='KHz', f_field=tag)
                    elif tag == 'TransmitSweepRateHz':
                        metadata['transmit']['sweep_rate'] = as_dict(value=float(value), unit='Hz', f_field=tag)

                    # Pattern metadata
                    elif tag == 'PatternType':
                        metadata['pattern']['type'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternDate':
                        metadata['pattern']['date'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternResolution':
                        scale, unit = value.split()
                        metadata['pattern']['resolution'] = as_dict(value=float(scale), unit=unit, f_field=tag)
                    elif tag == 'PatternSmoothing':
                        scale, unit = value.split()
                        metadata['pattern']['smoothing'] = as_dict(value=float(scale), unit=unit, f_field=tag)
                    elif tag == 'PatternAmplitudeCorrections':
                        value = [float(el) for el in value.split()]
                        metadata['pattern']['ampl_corr'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternPhaseCorrections':
                        value = [float(el) for el in value.split()]
                        metadata['pattern']['phase_corr'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternAmplitudeCalculations':
                        value = [float(el) for el in value.split()]
                        metadata['pattern']['ampl_calc'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternPhaseCalculations':
                        value = [float(el) for el in value.split()]
                        metadata['pattern']['phase_calc'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternMethod':
                        metadata['pattern']['phase_calc'] = as_dict(value=value, f_field=tag)

                    # Radial metadata
                    elif tag == 'RadialBraggPeakDropOff':
                        metadata['radial']['bragg_drop_off'] = as_dict(value=float(value), f_field=tag)
                    elif tag == 'RadialBraggPeakNull':
                        metadata['radial']['bragg_peak_null'] = as_dict(value=float(value), f_field=tag)
                    elif tag == 'RadialBraggNoiseThreshold':
                        metadata['radial']['bragg_noise_threshold'] = as_dict(value=value, f_field=tag)

                    # Table data (column names), and validation metadata parsing
                    elif tag == 'TableColumnTypes' and tab_flag:
                        col_names = value.split()
                    elif tag == 'TableColumns' and tab_flag:
                        tmp['col_num'] = int(value)
                    elif tag == 'TableRows' and tab_flag:
                        tmp['row_num'] = int(value)
                    elif tag == 'TableEnd:' and tab_flag:
                        tab_flag = False

                    # Other different metadata
                    elif tag == 'DopplerResolutionHzPerBin':
                        metadata['other']['doppler_resol'] = as_dict(value=float(value), unit='Hz/bin',
                                                                          f_field=tag)
                    elif tag == 'RangeResolutionKMeters':
                        metadata['other']['range_resol'] = as_dict(value=float(value), unit='km', f_field=tag)
                    elif tag == 'CurrentVelocityLimit':
                        # <tvf> file contains units for the field, while <rvf> files does not.
                        # So i we can extract two values from tre field we will do that, else: take only scale
                        try:
                            scale, unit = value.split()
                            metadata['other']['current_vel_lim'] = as_dict(value=float(scale), unit=unit, f_field=tag)
                        except ValueError:
                            metadata['other']['current_vel_lim'] = as_dict(value=float(value), f_field=tag)

                # If False - we got a line from the table => parse it and add to the <data> array
                elif line[0] is not '%' and tab_flag:
                    data.append([float(el.strip()) for el in line.strip().split()])

        # Validation of data reading
        # Since the input file contains some data as numbers of columns and rows in the table
        # we can make validation of accumulated data by that parameters

        if len(data) == 0:
            raise EmptyFile

        if len(col_names) != tmp['col_num']:
            raise ValueError

        if len(data) != tmp['row_num']:
            raise ValueError

        elif len(data[0]) != tmp['col_num']:
            raise ValueError

        return col_names, data, metadata

    def get_time_coverage(self):
        """Time coverage of data file from metadata"""
        dt = timedelta(0, 0, 0, 0, self.metadata['time']['coverage']['value'])
        time_start = self.metadata['time']['stamp']['value']
        self.time_coverage = (time_start, time_start + dt)

    def get_geolocation(self):
        """Geolocation in format tuple()"""
        lon_min = self.data.T[0].min()
        lon_max = self.data.T[0].max()

        lat_min = self.data.T[1].min()
        lat_max = self.data.T[1].max()

        self.geolocation = ((lon_min, lat_min),
                            (lon_min, lat_max),
                            (lon_max, lat_max),
                            (lon_max, lat_min),
                            (lon_min, lat_min),)
