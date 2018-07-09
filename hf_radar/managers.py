from django.db import models
import os
from django.contrib.gis.geos import LineString
from geospaas.utils import validate_uri, nansat_filename
from geospaas.vocabularies.models import Platform, Instrument, DataCenter, ISOTopicCategory
from geospaas.catalog.models import GeographicLocation, Source, Dataset, DatasetURI
from hf_radar.toolbox.utils import get_data
import warnings
from hf_radar.toolbox.utils import AlreadyExists


class BaseManager(models.Manager):

    def set_metadata(self):
        """
        :param plat: platform name from the metadata
        :return:
        """
        # The platform and instrument metadata are not in the metadata
        # Thus we will have to set it manually
        platform = Platform.objects.get_by_natural_key(short_name='CODAR')
        instrument = Instrument.objects.get(short_name='SCR-HF')
        src = Source.objects.get_or_create(platform=platform,
                                           instrument=instrument)[0]
        dc = DataCenter.objects.get(short_name='NO/MET')
        iso = ISOTopicCategory.objects.get(name='Oceans')

        return dc, iso, src


class DatasetManager(BaseManager):

    def get_or_create(self, uri, **options):

        """ Create all datasets from given file and add corresponding metadata
        Parameters:
        ----------
            uri_data : str

        Returns:
        -------
            count : Number of ingested buoy datasets
        """

        # clean input uri from file://localhost/
        # uri = nansat_filename(uri)

        # Is the file in the database
        if DatasetURI.objects.filter(uri=uri):
            raise AlreadyExists

        # Get type of data.
        # Parse input path to file: (1) Get filename; (2) Get format
        uri_file_format = os.path.split(uri)[-1].split('.')[-1]
        # If a file format is <rvl> then that's Radial Map
        # Else if file format is <tvf> then Current Map
        if uri_file_format == 'rvf':
            title = 'Radial map'
        elif uri_file_format == 'tvf':
            title = 'Current map'
        else:
            raise NameError('The input file has a not supported format')

        dataset = get_data(uri)

        if dataset == -1:
            raise warnings.warn('The file does not contain data')

        data_center, iso, source = self.set_metadata()

        geometry = LineString(dataset.geolocation)
        geoloc, geo_cr = GeographicLocation.objects.get_or_create(geometry=geometry)

        # Create object in database
        ds, ds_cr = Dataset.objects.get_or_create(
            entry_title=title,
            ISO_topic_category=iso,
            data_center=data_center,
            summary='',
            time_coverage_start=dataset.time_coverage[0],
            time_coverage_end=dataset.time_coverage[1],
            source=source,
            geographic_location=geoloc)

        if ds_cr:
            data_uri, duc = DatasetURI.objects.get_or_create(uri=uri, dataset=ds)

        return ds, ds_cr


class FinnmarkDatasetManager(BaseManager):
    pass
