from django.core.management.base import BaseCommand

from geospaas.utils import uris_from_args
from geospaas.catalog.models import Dataset as CatalogDataset
from hf_radar.models import Dataset


class Command(BaseCommand):
    args = '<filename>'
    help = 'Add WS file to catalog archive and make png images for ' \
           'display in Leaflet'

    def add_arguments(self, parser):
        parser.add_argument('--reprocess',
                            action='store_true',
                            help='Force reprocessing')

    def handle(self, *args, **options):

        for non_ingested_uri in uris_from_args(*args):

            self.stdout.write('Ingesting %s ...\n' % non_ingested_uri)
            ds, cr = Dataset.objects.get_or_create(non_ingested_uri, **options)

            if not type(ds) == CatalogDataset:
                self.stdout.write('Not found: %s\n' % non_ingested_uri)
            elif cr:
                self.stdout.write('Successfully added: %s\n' % non_ingested_uri)
            else:
                self.stdout.write('Was already added: %s\n' % non_ingested_uri)
