from urllib.request import urlretrieve
from datetime import datetime
from calendar import monthrange
import os

# Constants
OpedDAP_ROOT = 'https://thredds.met.no/thredds/fileServer/remotesensinghfradar/'
origin = 'FRUH'
dst_root = os.path.join('/src/.devcontainer/data', origin)
YEARS = [2018]
MONTHS = [1]


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    create_dir(dst_root)
    for year in YEARS:
        dst_year = os.path.join(dst_root, str(year))
        create_dir(dst_year)
        for month in MONTHS:
            dst_month = os.path.join(dst_year, str(month))
            create_dir(dst_month)
            for day in range(1, monthrange(year, month)[-1] + 1):
                dst_day = os.path.join(dst_month, str(day))
                create_dir(dst_day)

                date = datetime(year, month, day)
                dst = os.path.join(dst_day)
                create_dir(dst)
                date = datetime(year, month, day)
                print('Date: ' + date.isoformat())
                filename = 'RDLm_FRUH_%d_%.2d_%.2d.nc' % (year, month, day)
                url = os.path.join(OpedDAP_ROOT, str(year), '%.2d' % month, '%.2d' %day, origin, filename)
                file_dst = os.path.join(dst_day, filename)
                if os.path.exists(file_dst):
                    print('Already exists: %s' % file_dst)
                else:
                    try:
                        print('URL: %s' % url)
                        print('DST: %s' % file_dst)
                        urlretrieve(url, file_dst)
                    except IOError:
                        print('Error')
                        pass
    print('END!')

