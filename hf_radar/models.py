from __future__ import unicode_literals

from django.db import models
from geospaas.catalog.models import Dataset as CatalogDataset
from hf_radar.managers import DatasetManager


class Dataset(CatalogDataset):

    lat = models.FloatField(null=False, verbose_name='Latitude')
    lon = models.FloatField(null=False, verbose_name='Longitude')

    u = models.FloatField(null=False, verbose_name='Velocity U')
    v = models.FloatField(null=False, verbose_name='Velocity V')

    objects = DatasetManager()

    class Meta:
        proxy = True
