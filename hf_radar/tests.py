from django.test import TestCase
from models import FinnmarkDatasetManager
from managers import BaseManager
from toolbox.utils import AlreadyExists
from geospaas.vocabularies.models import Platform, Instrument, DataCenter, ISOTopicCategory
from geospaas.catalog.models import GeographicLocation, DatasetURI, Source, Dataset
from datetime import datetime, timedelta
import pytz


class BaseMangerTest(TestCase):
    fixtures = ['vocabularies', 'hf_platform', 'hf_data']

    def test_set_metadata(self):
        dc, iso, src = BaseManager.set_metadata()
        self.assertIsInstance(src, Source)
        self.assertEqual(src.platform.short_name, 'CODAR')
        self.assertEqual(src.instrument.short_name, 'SCR-HF')
        self.assertIsInstance(dc, DataCenter)
        self.assertEqual(dc.short_name, 'NO/MET')
        self.assertIsInstance(iso, ISOTopicCategory)
        self.assertEqual(iso.name, 'Oceans')

    def test_check_in_db(self):
        test_uri = "/test/path/to/file/test.nc"
        with self.assertRaises(AlreadyExists):
            BaseManager.check_in_db(test_uri)


class FinnmarkDatasetManagerTest(TestCase):
    fixtures = ['vocabularies', 'hf_platform']

    def test_get_or_create(self):
        test_uri = '/vagrant/shared/src/django-geo-spaas-hf-radar/test_data/RDLm_FRUH_2017_10_19.nc'
        dataset = FinnmarkDatasetManager().get_or_create(test_uri)

        db_data = Dataset.objects.all()

        # file contains hourly data for a day
        self.assertEqual(len(db_data), 24)
        map(lambda i: self.assertEqual(i.dataseturi_set.first().uri, test_uri), db_data)
        # generate a list of expected timestamps
        t = [pytz.utc.localize(datetime(2017, 10, 19) + timedelta(hours=i)) for i in range(24)]
        map(lambda i: self.assertEqual(db_data[i].time_coverage_start, t[i]), range(len(db_data)))
        map(lambda i: self.assertEqual(db_data[i].time_coverage_end, t[i] + timedelta(hours=1)),
            range(len(db_data)))
        self.assertEqual(db_data[0].entry_title, 'Near-Real Time Surface Ocean Radial Velocity')
        expected_geoloc = "SRID=4326;POLYGON ((22.585538 72.640176, 23.323767 72.71219600000001, " \
                          "24.061995 72.782293, 24.800224 72.85047, 25.538452 72.916724, 26.276681 " \
                          "72.981056, 27.014909 73.04346700000001," \
        " 27.753138 73.103956, 28.491366 73.16252299999999, 29.229595 73.219168, 30.336938 73.300533," \
        " 30.336938 73.300533, 29.582044 72.102228, 28.580677 71.16030000000001, 27.332837 70.47475," \
        " 25.838522 70.04557699999999, 24.097734 69.872781, 22.110472 69.956363, 19.876737 70.296322," \
        " 17.396527 70.892658, 14.669844 71.74537100000001, 11.696687 72.854462, 11.696687 72.854462," \
        " 13.050106 73.01738899999999, 13.952386 73.123604, 14.854665 73.227898, 15.756944 73.33027, " \
        "16.659224 73.43071999999999, 17.561503 73.529248, 18.463782 73.625854, 19.366062 73.720539, " \
        "20.268341 73.81330199999999, 21.17062 73.904143, 21.17062 73.904143, 22.421244 72.624048, " \
        "23.425394 71.600331, 24.18307 70.83299100000001, 24.694272 70.322028, 24.959001 70.067443," \
        " 24.977256 70.06923500000001, 24.749037 70.327404, 24.274344 70.84195099999999, 23.553178 " \
        "71.612875, 22.585538 72.640176))"

        self.assertEqual(db_data[0].geographic_location.geometry.ewkt, expected_geoloc)
