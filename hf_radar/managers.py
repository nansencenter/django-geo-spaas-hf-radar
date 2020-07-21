import os
from django.db.models import Manager
from django.contrib.gis.geos import Polygon
from django.utils.timezone import make_aware
from geospaas.catalog.managers import FILE_SERVICE_NAME, LOCAL_FILE_SERVICE 
from geospaas.utils.utils import validate_uri, nansat_filename
from geospaas.catalog.models import GeographicLocation, Source, Dataset, DatasetURI
from geospaas.vocabularies.models import (Platform, Instrument, DataCenter,
                                          ISOTopicCategory, Location)
from datetime import datetime, timedelta
from nansat import Domain, Nansat
import json
import uuid
import pythesint as pti


class HFRDatasetManager(Manager):

    def get_or_create(self, uri, force):
        # Validate uri - this should raise an exception if the uri doesn't 
        # point to a valid file or stream
        validate_uri(uri)
        # Several datasets can refer to the same uri (e.g., scatterometers and svp drifters), so we
        # need to pass uri_filter_args
        uris = DatasetURI.objects.filter(uri=uri)
        # If the ingested uri is already in the database and not <force> ingestion then stop
        if uris.exists() and not force:
            return uris[0].dataset, False
        elif uris.exists() and force:
            uris[0].dataset.delete()
        # Open file with Nansat
        n = Nansat(nansat_filename(uri))
        # get metadata from Nansat and get objects from vocabularies
        n_metadata = n.get_metadata()
        # set compulsory metadata (source)
        platform, _ = Platform.objects.get_or_create(json.loads(n_metadata['platform']))
        instrument, _ = Instrument.objects.get_or_create(json.loads(n_metadata['instrument']))
        specs = n_metadata.get('specs', '')
        source, _ = Source.objects.get_or_create(platform=platform,
                                                 instrument=instrument,
                                                 specs=specs)
        footprint = Polygon(list(zip(*n.get_border())))
        geolocation = GeographicLocation.objects.get_or_create(geometry=footprint)[0]
        data_center = DataCenter.objects.get_or_create(json.loads(n_metadata['Data Center']))[0]
        iso_category = ISOTopicCategory.objects.get_or_create(pti.get_iso19115_topic_category('Oceans'))[0]
        location = Location.objects.get_or_create(json.loads(n_metadata['gcmd_location']))[0]
        # create dataset
        ds, created = Dataset.objects.get_or_create(
                time_coverage_start=make_aware(n.time_coverage_start),
                time_coverage_end=make_aware(n.time_coverage_start + timedelta(hours=23, minutes=59, seconds=59)),
                source=source,
                geographic_location=geolocation,
                ISO_topic_category=iso_category,
                data_center=data_center,
                summary='',
                gcmd_location=location,
                access_constraints='',
                entry_id=lambda: 'NERSC_' + str(uuid.uuid4()))
                
        ds_uri, _ = DatasetURI.objects.get_or_create(
            name=FILE_SERVICE_NAME, service=LOCAL_FILE_SERVICE, uri=uri, dataset=ds)
        return ds, created
