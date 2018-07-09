from __future__ import unicode_literals

from django.db import models
from geospaas.catalog.models import Dataset as CatalogDataset
from hf_radar.managers import DatasetManager, FinnmarkDatasetManager


class HfRatarFedjeDataset(CatalogDataset):

    objects = DatasetManager()

    class Meta:
        proxy = True


class HfRatarFinnmarkDataset(CatalogDataset):

    objects = FinnmarkDatasetManager()

    class Meta:
        proxy = True
