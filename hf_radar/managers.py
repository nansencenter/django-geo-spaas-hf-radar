from django.db import models

import numpy as np
import pandas as pd
from datetime import datetime

from geospaas.vocabularies.models import Platform, Instrument, DataCenter, ISOTopicCategory
from geospaas.catalog.models import GeographicLocation, Source


class DatasetManager(models.Manager):

    def set_metadata(self, inst):

        # TODO: Get instrument info from metadata
        platform = Platform.objects.get(short_name='HF-RADAR')
        instrument = Instrument.objects.get(short_name=inst)
        src = Source.objects.get_or_create(platform=platform,
                                           instrument=instrument)[0]
        # TODO: How to get data center
        data_center = DataCenter.objects.get(short_name='DOC/NOAA/OAR/AOML')
        iso = ISOTopicCategory.objects.get(name='Oceans')

    def get_data(self, uri):
        data = open(uri, 'r')

        if data.readline().strip()[0] is '%':
            data.close()
            columns, data, metadata = self.mapper_new_data(uri)
        else:
            data.close()
            columns, data, metadata = self.mapper_old_data(uri)

        return columns, data, metadata

    def add_hf_radar_data(self, uri, min_lat=None, max_lat=None,
                          min_lon=None, max_lon=None):

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


        # set metadata
        pass
