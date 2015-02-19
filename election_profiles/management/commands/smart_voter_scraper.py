#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
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

contestlists = ['city','school']

def request_url_in(target_url):
    """
    Looks up all contests by city, then by school district, and compiles the results into a single CSV file.
    """
    rows = []

    for n in contestlists:
        result = requests.get(target_url + n + '.html')
        content = result.content
        soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
        rowcluster = fetch_all_contests(soup)
        for row in rowcluster:
            rows.append(row)
    #logger.debug(len(rows))

    #print_to_CSV(filter_la(rows))
    #print_to_json(filter_la(rows))
    check_db(filter_la(rows))

def filter_la(rows):
    la_rows = []
    for r in range(len(rows)):
        if re.search("Los Angeles",rows[r]['contest']) and not re.search("Trustees",rows[r]['contest']):
            la_rows.append(rows[r])
    return la_rows

def list2string(listdata):
    lst = ""
    for l in range(len(listdata)):
        lst += "\"" + listdata[l] + "\""
        if l + 1 != len(listdata):
            lst += ","
    return lst

def get_kpcc_qa(candidate):
    """
    Set up links to KPCC interviews here
    """
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

def simplify_contest_name(contestlong):
    # Clean up contest name
    conteststrings = contestlong.split(';')
    if re.search("Council",conteststrings[0]):
        contest = "City Council" + conteststrings[2]
    else:
        contest = "LAUSD School Board" + conteststrings[2]
    return contest

def print_to_json(rows):
    jsonlist = {}
    jsonlist['candidates'] = []
    for r in range(len(rows)):
        candidate = rows[r]['candidate']
        contest = simplify_contest_name(rows[r]['contest'])
        kpcc_qa_url = get_kpcc_qa(candidate)

        # Create json object
        jobj = {}
        jobj['candidate'] = candidate
        jobj['contest'] = contest
        jobj['biofacts'] = rows[r]['biofacts']
        jobj['priorities'] = rows[r]['priorities']
        jobj['questions_url'] = rows[r]['questions_url']
        jobj['candidate_url'] = rows[r]['candidate_url']
        jobj['kpcc_qa_url'] = kpcc_qa_url
        jsonlist['candidates'].append(jobj)
    #logger.debug(contestobj)

    jsondata = json.dumps(jsonlist, encoding="utf-8", indent=4, separators=(',', ': '))

    # Write to file
    ofile = open("election_profiles/data/smartvoter.json","w")
    ofile.write(jsondata)
    ofile.close()

def slugify_name(value):
    value = value.encode("ascii", "ignore").lower().strip().replace(" ", "-")
    value = re.sub(r"[^\w-]", "", value)
    return value

def check_db(rows):

    for candidate in rows:
        logger.debug(candidate)

        try:
            obj, created = Candidate.objects.get_or_create(
                candidate = candidate["candidate"],
                defaults = {
                    "candidate_slug": slugify_name(candidate["candidate"]),
                    "contest": simplify_contest_name(candidate['contest']),
                    "biofacts": candidate["biofacts"],
                    "priorities": candidate["priorities"],
                    "questions_url": candidate["questions_url"],
                    "candidate_url": candidate["candidate_url"],
                    "kpcc_qa_url": get_kpcc_qa(candidate["candidate"]),
                }
            )
            if not created:
                print "%s exists. Checking for updates..." % (candidate["candidate"])
                #logger.debug(obj.biofacts)
            elif created:
                print "%s created" % (candidate["candidate"])
        except ValueError, exception:
            #traceback.print_exc(file=sys.stdout)
            print "%s-%s" % (exception, candidate["candidate"])
            logger.debug("%s-%s" % (exception, candidate["candidate"]))


def print_to_CSV(rows):
    headers = ['candidate','contest','biofacts','priorities','questions_url','candidate_url']
    write_data(headers,rows)

def fetch_sample_candidate():
    """
    As a way to test the scraper, fetches info specifically for Robert L. Cole.
    """
    rows = []
    contestname = "Council Member; City of Los Angeles; District 8"
    candidate_name = "Robert L. Cole, Jr."
    candidate_url = "http://www.smartvoter.org/2015/03/03/ca/la/vote/cole_r/"
    candidate_rows = fetch_candidate_info(candidate_name,candidate_url,contestname)
    #logging.debug(candidate_rows)

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
        lst.append(i.text.encode('utf-8'))
    return lst

def write_data(headers,data):
    ofile = open('output/smartvoter.csv',"wb")
    writer = csv.writer(ofile,delimiter=',',quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(headers)

    for row in data:
        writer.writerow(row)
    
    ofile.close()
