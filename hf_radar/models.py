from __future__ import unicode_literals

from django.db import models
from geospaas.catalog.models import Dataset as CatalogDataset
from hf_radar.managers import HFRDatasetManager

class HFRDataset(CatalogDataset):

    objects = HFRDatasetManager()

    class Meta:
        proxy = True
