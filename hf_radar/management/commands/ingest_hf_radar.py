from django.core.management.base import BaseCommand
from geospaas.catalog.models import Dataset as CatalogDataset
from hf_radar.models import HFRDataset
from datetime import datetime 
from geospaas.utils.utils import uris_from_args


class Command(BaseCommand):
    args = '<filename>'
    help = 'Add WS file to catalog archive and make png images for ' \
           'display in Leaflet'

    def add_arguments(self, parser):
        # Input files
        parser.add_argument('input_files', nargs='*', type=str)


    def handle(self, *args, **options):
        start_time = datetime.now()
        non_ingested_uris = uris_from_args(options['input_files'])
        uri_id = 1
        for non_ingested_uri in non_ingested_uris:
            print('[%.4d/%.4d] | %s' % (uri_id, len(non_ingested_uris), non_ingested_uri), end=' | ')
            ds, cr = HFRDataset.objects.get_or_create(non_ingested_uri)
            print(datetime.now() - start_time, end=' | ')
            if cr:
                print(self.style.SUCCESS('OK'))
            elif ds:
                print(self.style.WARNING('SKIP'))
            else:
                print(self.style.ERROR('FAILED'))
            uri_id += 1
