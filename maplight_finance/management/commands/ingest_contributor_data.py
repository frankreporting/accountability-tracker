from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from django.core.mail import send_mail, mail_admins, send_mass_mail, EmailMessage
from django.conf import settings
from maplight_finance.models import Initiative, InitiativeContributor
import os
import csv
import logging
import time
import datetime
import urllib2
import requests
import string
from datetime import tzinfo
from dateutil import parser

logger = logging.getLogger("accountability_tracker")

local_testing_map_light_csvs = [
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-1-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-2-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-45-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-46-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-47-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-48-funding_20140924.csv"
]

class MapLightApi(object):

    csv_prefix = "http://votersedge.org/files/ballot-measures/funding-csv/"
    url_prefix = "http://votersedge.org/services_open_api/cvg.contest_v1.json?"
    url_api_key = "apikey=%s" % (settings.MAP_LIGHT_API_KEY)
    url_query = "&contest=M193&date=2014-11-02"
    url_request = "%s%s%s" % (url_prefix, url_api_key, url_query)


    def _init(self, *args, **kwargs):

        """
        make a request to the Map Light API and return JSON data
        """

        #logger.debug(self.url_request)

        logger.debug(dir(settings))








class Command(BaseCommand):
    help = "Begin a request to the MapLight API"
    def handle(self, *args, **options):
        task_run = MapLightApi()
        task_run._init()
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
