#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This command will not work on its own yet. Needs to have class Command added and needs to fetch data
 from database and loop through it, adding each candidate to list 'rows'.
"""
from __future__ import division
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from election_profiles.models import Candidate
import logging
import re
import time
import datetime
from dateutil import parser

logger = logging.getLogger("accountability_tracker")

class CreateQAlinks(object):

    def _init(self, *args, **kwargs):
        qalinks = [
            {"name": "Scott Mark Schmerelson", "link": "http://www.scpr.org/blogs/education/2015/02/13/17911/lausd-school-board-candidate-survey-scott-mark-sch/"},
            {"name": "Ankur Patel", "link": "http://www.scpr.org/blogs/education/2015/02/13/17912/lausd-school-board-candidate-survey-ankur-patel-di/"},
            {"name": "Carl J. Petersen", "link": "http://www.scpr.org/blogs/education/2015/02/13/17913/lausd-school-board-candidate-survey-carl-petersen/"},
            {"name": "Andrew Thomas", "link": "http://www.scpr.org/news/2015/02/13/49832/lausd-school-board-candidate-survey-andew-thomas-d/"},
            {"name": "Richard A. Vladovic", "link": "http://www.scpr.org/news/2015/02/13/49833/lausd-school-board-candidate-survey-dr-richard-vla/"},
            {"name": "Filiberto Gonzalez", "link": "http://www.scpr.org/blogs/education/2015/02/13/17917/lausd-school-board-candidate-survey-filiberto-gonz/"},
            {"name": "Tamar Galatzan", "link": "http://www.scpr.org/blogs/education/2015/02/13/17919/lausd-school-board-candidate-surveytamar-galatzan/"},
            {"name": "Bennett Kayser", "link": "http://www.scpr.org/blogs/education/2015/02/13/17918/lausd-school-board-candidate-survey-bennett-kayser/"}
        ]

        for l in qalinks:
            try:
                obj = Candidate.objects.get(candidate=l["name"])
                obj.kpcc_qa_url = l["link"]
                obj.change_date = datetime.datetime.now()
                obj.save(update_fields=['kpcc_qa_url','change_date'])
                print "kpcc_qa_url for candidate %s has been updated to %s." % (l["name"],obj.kpcc_qa_url)
            except:
                print "There was a problem fetching the database object for candidate %s." % (l["name"])

    """
    Set up links to KPCC interviews here

    if candidate == "Scott Mark Schmerelson":
        kpcc_qa_url = "http://www.scpr.org/blogs/education/2015/02/13/17911/lausd-school-board-candidate-survey-scott-mark-sch/"
    elif candidate == "Ankur Patel":
        kpcc_qa_url = "http://www.scpr.org/blogs/education/2015/02/13/17912/lausd-school-board-candidate-survey-ankur-patel-di/"
    elif candidate == "Carl J. Petersen":
        kpcc_qa_url = "http://www.scpr.org/blogs/education/2015/02/13/17913/lausd-school-board-candidate-survey-carl-petersen/"
    elif candidate == "Andrew Thomas":
        kpcc_qa_url = "http://www.scpr.org/news/2015/02/13/49832/lausd-school-board-candidate-survey-andew-thomas-d/"
    elif candidate == "Richard A. Vladovic":
        kpcc_qa_url = "http://www.scpr.org/news/2015/02/13/49833/lausd-school-board-candidate-survey-dr-richard-vla/"
    elif candidate == "Filiberto Gonzalez":
        kpcc_qa_url = "http://www.scpr.org/blogs/education/2015/02/13/17917/lausd-school-board-candidate-survey-filiberto-gonz/"
    elif candidate == "Tamar Galatzan":
        kpcc_qa_url = "http://www.scpr.org/blogs/education/2015/02/13/17919/lausd-school-board-candidate-surveytamar-galatzan/"
    elif candidate == "Bennett Kayser":
        kpcc_qa_url = "http://www.scpr.org/blogs/education/2015/02/13/17918/lausd-school-board-candidate-survey-bennett-kayser/"
    else:
        kpcc_qa_url = ""
    return kpcc_qa_url
    """

class Command(BaseCommand):
    help = "Set and load links to KPCC candidate Q&A's"
    def handle(self, *args, **options):
        task_run = CreateQAlinks()
        task_run._init()
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))