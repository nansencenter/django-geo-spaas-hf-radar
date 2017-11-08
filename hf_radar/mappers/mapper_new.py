from datetime import datetime
from uttils import as_dict

class HFRadarMapper(object):

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

    def __init__(self):
        pass

    def mapper(self, uri):
        tmp = {}

        # There are several tables in a rvl file. We need only first.
        # We also need to get an information about col names only for first table
        # The <tab_flag> is used for excepting of data overwriting in similar fields

        tab_flag = True

        with open(uri, 'r') as data_file:
            for line in data_file:
                line = line.strip()
                if line[0] is '%':
                    try:
                        tag, value = [el.strip() for el in line.replace('%', '').split(': ')]
                    except ValueError:
                        tag = line.replace('%', '')
                    # General metadata parsing
                    if tag == 'FileType':
                        self.metadata['general']['type'] = as_dict(value=value, f_field=tag)
                    elif tag == 'UUID':
                        self.metadata['general']['id'] = as_dict(value=value, f_field=tag)
                    elif tag == 'Manufacturer':
                        self.metadata['general']['manufacture'] = as_dict(value=value, f_field=tag)
                    elif tag == 'Site':
                        self.metadata['general']['site'] = as_dict(value=value.split()[0], f_field=tag)

                    # Time metadata
                    elif tag == 'TimeStamp':
                        t_arr = value.split()
                        date_time = datetime(*[int(x) for x in t_arr])
                        self.metadata['time']['stamp'] = as_dict(value=date_time, f_field=tag)
                    elif tag == 'TimeZone':
                        self.metadata['time']['zone'] = as_dict(value=value, f_field=tag)
                    elif tag == 'TimeCoverage':
                        self.metadata['time']['zone'] = as_dict(value=value, unit='m', f_field=tag)

                    # Geolocation metadata
                    elif tag == 'Origin':
                        value = [float(el) for el in value]
                        self.metadata['geolocation']['origin'] = as_dict(value=value, unit='m', f_field=tag)
                    elif tag == 'GreatCircle':
                        self.metadata['geolocation']['great circle'] = as_dict(value=value.split(), unit='m',
                                                                               f_field=tag)
                    elif tag == 'GeodVersion':
                        self.metadata['geolocation']['geod version'] = as_dict(value=value.split(), unit='m',
                                                                               f_field=tag)

                    # Transmit metadata
                    elif tag == 'TransmitCenterFreqMHz':
                        self. metadata['transmit']['center_freq'] = as_dict(value=float(value), unit='MHz', f_field=tag)
                    elif tag == 'TransmitBandwidthKHz':
                        self.metadata['transmit']['band_width'] = as_dict(value=float(value), unit='KHz', f_field=tag)
                    elif tag == 'TransmitSweepRateHz':
                        self.metadata['transmit']['sweep_rate'] = as_dict(value=float(value), unit='Hz', f_field=tag)

                    # Pattern metadata
                    elif tag == 'PatternType':
                        self.metadata['pattern']['type'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternDate':
                        self.metadata['pattern']['date'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternResolution':
                        scale, unit = value.split()
                        self.metadata['pattern']['resolution'] = as_dict(value=float(scale), unit=unit, f_field=tag)
                    elif tag == 'PatternSmoothing':
                        scale, unit = value.split()
                        self.metadata['pattern']['smoothing'] = as_dict(value=float(scale), unit=unit, f_field=tag)
                    elif tag == 'PatternAmplitudeCorrections':
                        value = [float(el) for el in value.split()]
                        self.metadata['pattern']['ampl_corr'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternPhaseCorrections':
                        value = [float(el) for el in value.split()]
                        self.metadata['pattern']['phase_corr'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternAmplitudeCalculations':
                        value = [float(el) for el in value.split()]
                        self.metadata['pattern']['ampl_calc'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternPhaseCalculations':
                        value = [float(el) for el in value.split()]
                        self.metadata['pattern']['phase_calc'] = as_dict(value=value, f_field=tag)
                    elif tag == 'PatternMethod':
                        self.metadata['pattern']['phase_calc'] = as_dict(value=value, f_field=tag)

                    # Radial metadata
                    elif tag == 'RadialBraggPeakDropOff':
                        self.metadata['radial']['bragg_drop_off'] = as_dict(value=float(value), f_field=tag)
                    elif tag == 'RadialBraggPeakNull':
                        self.metadata['radial']['bragg_peak_null'] = as_dict(value=float(value), f_field=tag)
                    elif tag == 'RadialBraggNoiseThreshold':
                        self.metadata['radial']['bragg_noise_threshold'] = as_dict(value=value, f_field=tag)

                    # Table data and metadata parsing methods
                    elif tag == 'TableColumnTypes' and tab_flag:
                        self.col_names = value.split()
                    elif tag == 'TableColumns' and tab_flag:
                        tmp['col_num'] = int(value)
                    elif tag == 'TableRows' and tab_flag:
                        tmp['row_num'] = int(value)
                    elif tag == 'TableEnd:' and tab_flag:
                        tab_flag = False

                    # Other different metadata
                    elif tag == 'DopplerResolutionHzPerBin':
                        self.metadata['other']['doppler_resol'] = as_dict(value=float(value), unit='Hz/bin',
                                                                          f_field=tag)
                    elif tag == 'RangeResolutionKMeters':
                        self.metadata['other']['range_resol'] = as_dict(value=float(value), unit='km', f_field=tag)
                    elif tag == 'CurrentVelocityLimit':
                        scale, unit = value.split()
                        self.metadata['other']['current_vel_lim'] = as_dict(value=float(value), unit=unit, f_field=tag)

                elif line[0] is not '%' and tab_flag:
                    self.data.append(line.split())

        # Validation of data reading
        if len(self.col_names) != tmp['col_num']:
            raise ValueError

        if len(self.data) != tmp['row_num']:
            raise ValueError

        elif len(self.data[0]) != tmp['col_num']:
            raise ValueError
