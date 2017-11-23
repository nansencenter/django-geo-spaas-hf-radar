from mappers.hf_metno_new import HFRadarMapper as NewHfMapper
from mappers.hf_metno_old import HFRadarMapper as OldHfMapper


def get_data(uri):
    data_file = open(uri, 'r')

    if data_file.readline().strip()[0] is '%':
        data_file.close()
        data = NewHfMapper(uri)
    else:
        data_file.close()
        data = OldHfMapper(uri)

    return data


def foo():
    pass
