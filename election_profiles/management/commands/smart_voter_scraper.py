#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from election_profiles.models import Candidate
import logging
import csv
import re
import json
import requests
import time
import datetime
from dateutil import parser
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup, NavigableString

logger = logging.getLogger("accountability_tracker")

class Command(BaseCommand):
    help = "Scrape latest info on candidates from SmartVoter.org"
    def handle(self, *args, **options):
        request_url_in('http://www.smartvoter.org/2015/03/03/ca/la/')
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))

def request_url_in(target_url):
    """
    Looks up all contests by city, then by school district, and compiles the results into a single CSV file.
    """
    contestlists = ['city','school']
    rows = []

    for n in contestlists:
        result = requests.get(target_url + n + '.html')
        content = result.content
        soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
        rowcluster = fetch_all_contests(soup)
        for row in rowcluster:
            rows.append(row)

    check_db(filter_la(rows))

def fetch_all_contests(html):
    """
    Collects contest name and candidate list for each, then fetches info on 
    each candidate.
    """
    races = html.findAll('a', href=re.compile('race/'))
    race_total = len(races)
    candidate_base_url = "http://www.smartvoter.org/2015/03/03/ca/la/"
    
    rows = []
    
    for x in range(race_total):
        candidate_rows = []
        contestname = races[x].find('b').text.encode("utf-8")
        candidatelist = races[x].findNext('ul').findAll('li')
        for candidate in candidatelist:
            candidate_name = candidate.find('a').text.encode("utf-8")
            try:
                urlstring = candidate.find('a')['href']
                candidate_url = candidate_base_url + urlstring.encode(encoding='UTF-8',errors='strict')
            except:
                candidate_url = "none"
            candidate_row = fetch_candidate_info(candidate_name,candidate_url,contestname)
            rows.append(candidate_row)
    return rows

def fetch_candidate_info(candidate,target_url,contest):
    if target_url == "none":
        row = {
            'candidate':candidate,
            'contest':contest,
            'biofacts':[],
            'priorities':[],
            'questions_url':'',
            'candidate_url':''
        }
        return row
    else:
        result = requests.get(target_url)
        content = result.content
        soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
        return parse_fields_from(soup,candidate,contest,target_url)

def parse_fields_from(html,candidate,contest,candidate_url):
    """
    Collects the following info: biographical highlights, top priorities, Q&A
    """
    data = html.body.findAll('tr')
    
    biofacts = ""
    priorities = ""
    questions_url = ""
    
    for row in range(len(data)):
        cell = data[row].findNext('td')
        try:
            tablename = cell.table.text.encode('utf-8')
        except:
            tablename = "NONE"

        """
        Now search for the following sections using regex:
        'Biographical Highlights'
        'Top Priorities if Elected'
        'Questions on Issues'
        """
        if re.search("Biographical",tablename):
            biofacts = capture_list(cell)

        elif re.search("Priorities",tablename):
            priorities = capture_list(cell)

        elif re.search("Questions",tablename):
            questions_url = candidate_url + "questions.html"

    # Create a row as dictionary and return it to the full dataset
    row = {
        'candidate':candidate,
        'contest':contest,
        'biofacts':biofacts,
        'priorities':priorities,
        'questions_url':questions_url,
        'candidate_url':candidate_url
        }
    return row

def capture_list(data):
    listitems = data.findAll('li')
    lst = []
    for i in listitems:
        lst.append(i.text)
    return lst

def filter_la(rows):
    la_rows = []
    for r in range(len(rows)):
        if re.search("Los Angeles",rows[r]['contest']) and not re.search("Trustees",rows[r]['contest']):
            la_rows.append(rows[r])
    return la_rows

def check_db(rows):
    for candidate in rows:
        candidate["contest"] = simplify_contest_name(candidate["contest"])
        candidate["candidate"] = candidate["candidate"].decode(encoding='UTF-8',errors='strict')

        try:
            obj, created = Candidate.objects.get_or_create(
                candidate = candidate["candidate"],
                contest = candidate["contest"],
                defaults = {
                    "candidate_slug": slugify_name(candidate["candidate"]),
                    "biofacts": candidate["biofacts"],
                    "priorities": candidate["priorities"],
                    "questions_url": candidate["questions_url"],
                    "candidate_url": candidate["candidate_url"],
                }
            )
            if not created:
                print "%s exists. Checking for updates..." % (candidate["candidate"])
                for x in candidate:
                    if not candidate[x] and getattr(obj,x):
                        print "SmartVoter's %s info for candidate %s may have been deleted." % (x,candidate["candidate"])
                    elif candidate[x] and getattr(obj,x) and candidate[x] != getattr(obj,x):
                        setattr(obj,x,candidate[x])
                        obj.change_date = timezone.now()
                        obj.save(update_fields=[x,'change_date'])
                        print "%s info for candidate %s has been updated." % (x,candidate["candidate"])
                    elif candidate[x] and not getattr(obj,x):
                        setattr(obj,x,candidate[x])
                        obj.change_date = timezone.now()
                        obj.save(update_fields=[x,'change_date'])
                        print "%s info for candidate %s has been updated." % (x,candidate["candidate"])

            elif created:
                print "%s created" % (candidate["candidate"])
        except ValueError, exception:
            #traceback.print_exc(file=sys.stdout)
            print "%s-%s" % (exception, candidate["candidate"])
            logger.debug("%s-%s" % (exception, candidate["candidate"]))

def simplify_contest_name(contestlong):
    # Clean up contest name
    try:
        conteststrings = contestlong.split(';')
        if re.search("Council",conteststrings[0]):
            contest = "City Council" + conteststrings[2]
        else:
            contest = "LAUSD School Board" + conteststrings[2]
    except:
        contest = contestlong
    return contest

def slugify_name(value):
    value = value.encode("ascii", "ignore").lower().strip().replace(" ", "-")
    value = re.sub(r"[^\w-]", "", value)
    return value