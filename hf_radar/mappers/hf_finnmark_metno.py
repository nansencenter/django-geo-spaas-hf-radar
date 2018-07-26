from netCDF4 import Dataset
from scipy.interpolate import griddata
from datetime import datetime, timedelta
import numpy as np
from nansat import Nansat, Domain


class HFRadar(object):
    PX_SIZE = 4000  # Pixel size in meters
    TIME_VARS = ['direction', 'ersc', 'ertc', 'espc', 'etmp', 'maxv',
                 'minv', 'sprc', 'u', 'v', 'velo', 'vflg', 'xdst', 'ydst']

    def __init__(self, filename, timestamp):
        self.filename = filename
        self.timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')

        dataset = Dataset(self.filename)

        # Create a dst grid
        x_dst_grd, y_dst_grd = self.create_linear_grid(dataset)

        x_src_grd = dataset.variables['x'][:]
        y_src_grd = dataset.variables['y'][:]

        d = Domain('+proj=utm +zone=34 +ellps=WGS84 +datum=WGS84 +units=m +no_defs',
                   '-te %f %f %f %f -tr %d %d' % (x_src_grd.min(), y_src_grd.min(),
                                                  x_src_grd.max(), y_src_grd.max(),
                                                  self.PX_SIZE, self.PX_SIZE))

        n = Nansat.from_domain(d)

        time_id = self.get_time_id(dataset)

        for var_key in self.TIME_VARS:
            var = dataset.variables[var_key][time_id]
            repr_var = self.reproject((x_src_grd, y_src_grd), var,
                                      (x_dst_grd, y_dst_grd))
            if var_key == 'vflg': repr_var = np.int32(repr_var)
            var_metadata = self.get_band_metadata(dataset, var_key)
            n.add_band(repr_var, parameters=var_metadata)

        self.data = n

    def create_linear_grid(self, dataset):
        x = dataset.variables['x'][:]
        y = dataset.variables['y'][:]
        x_grd, y_grd = np.meshgrid(np.arange(x.min(), x.max(), self.PX_SIZE),
                                   np.arange(y.max(), y.min(), self.PX_SIZE * -1))
        return x_grd, y_grd

    def reproject(self, src_grd, var, dst_grd):
        # Points [(x, y), ... , ] from original file
        points = np.array(zip(src_grd[0].flatten(), src_grd[1].flatten()))
        repr_var = griddata(points, var.flatten(), (dst_grd[0], dst_grd[1]), method='nearest')
        return repr_var

    def get_band_metadata(self, dataset, var):
        band_ds = dataset.variables[var]
        parameters = {'name': var}
        for attr in band_ds.ncattrs():
            parameters[attr] = band_ds.getncattr(attr)
        return parameters

    def get_time_id(self, dataset):
        time_origin = dataset.variables['time'].units.split()[-1]
        time_origin = datetime.strptime(time_origin, '%Y-%m-%d')
        file_times = [time_origin + timedelta(seconds=int(sec)) for sec in
                      dataset.variables['time'][:]]

        try:
            src_time_id = file_times.index(self.timestamp)
        except ValueError:
            ValueError('Not found: %s' % self.timestamp.isoformat())

        return src_time_id
