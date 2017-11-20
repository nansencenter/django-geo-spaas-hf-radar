from django.db import models

import numpy as np
import pandas as pd
import os
from datetime import datetime
from django.contrib.gis.geos import LineString

from geospaas.vocabularies.models import Platform, Instrument, DataCenter, ISOTopicCategory
from geospaas.catalog.models import GeographicLocation, Source, Dataset
from mappers.hf_metno_new import HFRadarMapper as NewHfMapper
from mappers.hf_metno_old import HFRadarMapper as OldHfMapper


class DatasetManager(models.Manager):
    # TODO: Standardization of column names

    def set_metadata(self):
        """
        :param plat: platform name from the metadata
        :return:
        """
        # The platform and instrument metadata are not in the metadata.
        # Thus we will have to set it manually
        platform = Platform.objects.get_by_natural_key(short_name='CODAR')
        instrument = Instrument.objects.get(short_name='HF-RADAR')
        src = Source.objects.get_or_create(platform=platform,
                                           instrument=instrument)[0]
        dc = DataCenter.objects.get(short_name='MET.NO')
        iso = ISOTopicCategory.objects.get(name='Oceans')

        return dc, iso, src

    def get_data(self):

        data_file = open(self.uri, 'r')

        if data_file.readline().strip()[0] is '%':
            data_file.close()
            data = NewHfMapper(self.uri)
        else:
            data_file.close()
            data = OldHfMapper(self.uri)

        return data

    def get_or_create(self, uri):

        """ Create all datasets from given file and add corresponding metadata
        Parameters:
        ----------
            uri_data : str
                URI to file
            uri_metadata : str
                URI to metadata file
            time_coverage_start : timezone.datetime object
                Optional start time for ingestion
            time_coverage_end : timezone.datetime object
                Optional end time for ingestion
        Returns:
        -------
            count : Number of ingested buoy datasets
        """
        # Get type of data.
        # Parse input path to file: (1) Get filename; (2) Get format
        uri_file_format = os.path.split(uri)[-1].split('.')[-1]

        # If a file format is <rvl> then that's Radial Map
        # Else if file format is <tvf> then Current Map
        if uri_file_format is 'rvl':
            title = 'Radial map'
        elif uri_file_format is 'tvf':
            title = 'Current map'
        else:
            raise IOError('The input file has wrong format')

        dataset = self.get_data()

        data_center, iso, source = self.set_metadata()

        geolocation = LineString(dataset.geolocation)

        # Create object in database
        ds, ds_cr = Dataset.objects.get_or_create(
            entry_title=title,
            ISO_topic_category=iso,
            data_center=data_center,
            summary='',
            time_coverage_start=dataset.time_coverage[0],
            time_coverage_end=dataset.time_coverage[1],
            source=source,
            geographic_location=geolocation)

        return ds
