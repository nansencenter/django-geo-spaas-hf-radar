from django.test import TestCase
from models import FinnmarkDatasetManager
from managers import BaseManager
from toolbox.utils import AlreadyExists
from geospaas.vocabularies.models import Platform, Instrument, DataCenter, ISOTopicCategory
from geospaas.catalog.models import GeographicLocation, DatasetURI, Source, Dataset
from netCDF4 import Dataset as netCDFDataset


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
        dataset = FinnmarkDatasetManager().get_or_create('/vagrant/shared/src/django-geo-spaas-hf-radar/test_data/RDLm_FRUH_2017_10_19.nc')
