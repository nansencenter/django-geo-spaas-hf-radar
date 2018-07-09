from django.db import models
import os
from django.contrib.gis.geos import LineString, Polygon
from geospaas.utils import validate_uri, nansat_filename
from geospaas.vocabularies.models import Platform, Instrument, DataCenter, ISOTopicCategory
from geospaas.catalog.models import GeographicLocation, Source, Dataset, DatasetURI
from hf_radar.toolbox.utils import get_data
import warnings
from hf_radar.toolbox.utils import AlreadyExists

from netCDF4 import Dataset as netCDFDataset
from datetime import datetime, timedelta
from nansat import Domain


class BaseManager(models.Manager):

    @staticmethod
    def set_metadata():
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

    @staticmethod
    def check_in_db(uri):
        if DatasetURI.objects.filter(uri=uri):
            raise AlreadyExists


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

    def get_or_create(self, uri, **options):
        # check if the file already exists in database
        BaseManager.check_in_db(uri)
        data_center, iso, source = BaseManager.set_metadata()
        dataset = netCDFDataset(uri)
        geometry = self.geolocation(dataset)
        geoloc, geo_cr = GeographicLocation.objects.get_or_create(geometry=geometry)
        timestamps = self.get_timestamps(dataset)

        for timestamp in timestamps:
            # Create object in database
            ds, ds_cr = Dataset.objects.get_or_create(
                entry_title=dataset.title,
                ISO_topic_category=iso,
                data_center=data_center,
                summary='',
                time_coverage_start=timestamp,
                time_coverage_end=timestamp + timedelta(hours=1),
                source=source,
                geographic_location=geoloc)

            if ds_cr:
                data_uri, duc = DatasetURI.objects.get_or_create(uri=uri, dataset=ds)

    def get_timestamps(self, dataset):
        time_metadata = dataset.variables['time'].units
        seconds_from = datetime.strptime(time_metadata.split()[-1], '%Y-%d-%m')

        timestemps_seconds = [int(timestp) for timestp in dataset.variables['time'][:]]
        time_stamps = [seconds_from + timedelta(seconds=sec) for sec in timestemps_seconds]
        return time_stamps

    def geolocation(self, dataset):
        d = Domain(lat=dataset.variables['lat'][:],
                   lon=dataset.variables['lon'][:])
        poly = Polygon(zip(*d.get_border()))
        return poly
