from __future__ import division
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from election_profiles.models import Candidate
import re
import logging
import time
import datetime
import requests
import json
from dateutil import parser

logger = logging.getLogger("accountability_tracker")

class CreateModelInstances(object):

    def _init(self, *args, **kwargs):

        with open("election_profiles/data/smartvoter.json") as json_file:
            json_data = json.load(json_file)

        for candidate in json_data["candidates"]:
            logger.debug(candidate)
            try:
                obj, created = Candidate.objects.get_or_create(
                    candidate = candidate["candidate"],
                    defaults = {
                        "candidate_slug": self._slugify_name(candidate["candidate"]),
                        "contest": candidate["contest"],
                        "biofacts": candidate["biofacts"],
                        "priorities": candidate["priorities"],
                        "questions_url": candidate["questions_url"],
                        "candidate_url": candidate["candidate_url"],
                    }
                )
                if not created:
                    print "%s exists" % (candidate["candidate"])
                elif created:
                    print "%s created" % (candidate["candidate"])
            except ValueError, exception:
                traceback.print_exc(file=sys.stdout)
                print "%s-%s" % (exception, candidate["candidate"])


    def _slugify_name(self, value):
        value = value.encode("ascii", "ignore").lower().strip().replace(" ", "-")
        value = re.sub(r"[^\w-]", "", value)
        return value


class Command(BaseCommand):
    help = "Begin a request to State Water Resources Board for latest usage report"
    def handle(self, *args, **options):
        task_run = CreateModelInstances()
        task_run._init()
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
