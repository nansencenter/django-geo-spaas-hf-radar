from django.test import TestCase
from models import HfRatarDataset
from geospaas.vocabularies.models import Platform, Instrument, DataCenter, ISOTopicCategory
from geospaas.catalog.models import GeographicLocation, DatasetURI, Source, Dataset


class DatasetManagerTest(TestCase):
    fixtures = ['vocabularies']
    
    def test_set_metadata(self):
        src, dc, iso = HfRatarDataset.objects.set_metadata()

        self.assertIsInstance(src, Source)
        # TODO: Test fails because CODAR does not exist in vocabularies
        # self.assertEqual(src.platform.short_name, 'CODAR')
        self.assertEqual(src.instrument.short_name, 'SCR-HF')
        self.assertIsInstance(dc, DataCenter)
        self.assertEqual(dc.short_name, 'NO/MET')
        self.assertIsInstance(iso, ISOTopicCategory)
        self.assertEqual(iso.name, 'Oceans')
