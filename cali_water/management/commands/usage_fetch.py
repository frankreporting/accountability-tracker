from __future__ import division
from django.conf import settings
from django.core.management.base import BaseCommand
import time
import datetime
import logging
from cali_water.usage_data_fetch import BuildMonthlyWaterUseReport

logger = logging.getLogger("accountability_tracker")

class Command(BaseCommand):
    help = "Begin a request to State Water Resources Board for latest usage report"
    def handle(self, *args, **options):
        task_run = BuildMonthlyWaterUseReport()
        task_run._init()
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
