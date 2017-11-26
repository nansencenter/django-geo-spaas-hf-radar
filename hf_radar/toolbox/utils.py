from hf_radar.mappers.hf_metno_new import HFRadarMapper as NewHfMapper
from hf_radar.mappers.hf_metno_old import HFRadarMapper as OldHfMapper


def get_data(uri):
    data_file = open(uri, 'r')

    if data_file.readline().strip()[0] is '%':
        data_file.close()
        dataset = NewHfMapper(uri)
    else:
        data_file.close()
        dataset = OldHfMapper(uri)

    return dataset
