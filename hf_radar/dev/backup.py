def get_data(uri):
    data = open(f_path, 'r')

    if data.readline().strip()[0] is '%':
        data.close()
        columns, data, metadata = mapper_new_data(uri)
    else:
        data.close()
        columns, data, metadata = mapper_old_data(uri)

    return columns, data, metadata


def _as_dict(value=None, unit=None, f_field=None):
    return {
        'value': value,
        'units': unit,
        'file field': f_field
    }


def mapper_new_data(uri):
    col_names = []
    data = []
    metadata = {'general': {},
                'time': {},
                'transmit': {},
                'pattern': {},
                'radial': {},
                'bragg': {},

                }
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
                    metadata['general']['type'] = _as_dict(value=value,
                                                           f_field=tag)

                elif tag == 'UUID':
                    metadata['general']['id'] = _as_dict(value=value,
                                                         f_field=tag)

                elif tag == 'Manufacturer':
                    metadata['general']['manufacture'] = _as_dict(value=value,
                                                                  f_field=tag)

                elif tag == 'Site':
                    metadata['general']['site'] = _as_dict(value=value.split()[0],
                                                           f_field=tag)

                # Time metadata
                elif tag == 'TimeStamp':
                    t_arr = value.split()
                    date_time = datetime(*[int(x) for x in t_arr])
                    metadata['time']['stamp'] = _as_dict(value=date_time,
                                                         f_field=tag)

                elif tag == 'TimeZone':
                    metadata['time']['zone'] = _as_dict(value=value,
                                                        f_field=tag)

                elif tag == 'TimeCoverage':
                    metadata['time']['zone'] = _as_dict(value=value,
                                                        unit='m',
                                                        f_field=tag)

                # Transmit metadata
                elif tag == 'TransmitCenterFreqMHz':
                    metadata['transmit']['center_freq'] = _as_dict(value=float(value),
                                                                   unit='MHz',
                                                                   f_field=tag)

                elif tag == 'TransmitBandwidthKHz':
                    metadata['transmit']['band_width'] = _as_dict(value=float(value),
                                                                  unit='KHz',
                                                                  f_field=tag)

                elif tag == 'TransmitSweepRateHz':
                    metadata['transmit']['sweep_rate'] = _as_dict(value=float(value),
                                                                  unit='Hz',
                                                                  f_field=tag)

                # Pattern metadata
                elif tag == 'PatternType':
                    metadata['pattern']['type'] = _as_dict(value=value,
                                                           f_field=tag)

                elif tag == 'PatternDate':
                    metadata['pattern']['date'] = _as_dict(value=value,
                                                           f_field=tag)
                elif tag == 'PatternResolution':
                    scale, unit = value.split()
                    metadata['pattern']['resolution'] = _as_dict(value=float(scale),
                                                                 unit=unit,
                                                                 f_field=tag)
                elif tag == 'PatternSmoothing':
                    scale, unit = value.split()
                    metadata['pattern']['smoothing'] = _as_dict(value=float(scale),
                                                                unit=unit,
                                                                f_field=tag)
                elif tag == 'PatternAmplitudeCorrections':
                    value = [float(el) for el in value.split()]
                    metadata['pattern']['ampl_corr'] = _as_dict(value=value,
                                                                f_field=tag)
                elif tag == 'PatternPhaseCorrections':
                    value = [float(el) for el in value.split()]
                    metadata['pattern']['phase_corr'] = _as_dict(value=value,
                                                                 f_field=tag)
                elif tag == 'PatternAmplitudeCalculations':
                    value = [float(el) for el in value.split()]
                    metadata['pattern']['ampl_calc'] = _as_dict(value=value,
                                                                f_field=tag)
                elif tag == 'PatternPhaseCalculations':
                    value = [float(el) for el in value.split()]
                    metadata['pattern']['phase_calc'] = _as_dict(value=value,
                                                                 f_field=tag)
                elif tag == 'PatternMethod':
                    metadata['pattern']['phase_calc'] = _as_dict(value=value,
                                                                 f_field=tag)



                # Table data and metadata parsing methods
                elif tag == 'TableColumnTypes' and tab_flag:
                    col_names = value.split()

                elif tag == 'TableColumns' and tab_flag:
                    tmp['col_num'] = int(value)

                elif tag == 'TableRows' and tab_flag:
                    tmp['row_num'] = int(value)

                elif tag == 'DopplerResolutionHzPerBin':
                    metadata['DopplerResolution'] = {
                        'value': float(value),
                        'units': 'Hz/bin'}

                elif tag == 'RangeResolutionKMeters':
                    metadata['RangeResolution'] = {
                        'value': float(value),
                        'units': 'km'}

                elif tag == 'TableEnd:' and tab_flag:
                    tab_flag = False

            elif line[0] is not '%' and tab_flag:
                data.append(line.split())

        # Validation of data reading
        if len(col_names) != tmp['col_num']:
            raise ValueError

        if len(data) != tmp['row_num']:
            raise ValueError

        elif len(data[0]) != tmp['col_num']:
            raise ValueError

    return col_names, data, metadata


def mapper_old_data(uri):
    col_names = []
    data = []
    metadata = {}
    return col_names, data, metadata
