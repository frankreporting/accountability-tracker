#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from election_profiles.models import Candidate, Measure, Contest
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
    Looks up all contests by city, school district and local ballot measure and then
    checks the info against the database, adding or updating as appropriate.
    """
    contestlists = ['city.html','school.html','meas']
    candidaterows = []
    measurerows = []
    contestrows = []

    for n in contestlists:
        result = requests.get(target_url + n)
        content = result.content
        soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
        if n == 'meas':
            rowcluster = fetch_measures(soup)
            if rowcluster:
                for row in rowcluster:
                    measurerows.append(row)
        else:
            rowsbatch = fetch_all_candidates(soup,n)
            for row in rowsbatch['contests']:
                contestrows.append(row)
            for row in rowsbatch['candidates']:
                candidaterows.append(row)

    if candidaterows:
        pass
        #add_or_update_candidates(filter_la(candidaterows))
    if measurerows:
        pass
        #add_or_update_measures(measurerows)
    if contestrows:
        add_or_update_contests(contestrows)

def add_or_update_contests(rows):
    for contest in rows:
        #measure["measure_number"] = measure["measure_number"].decode(encoding='UTF-8',errors='strict')
        try:
            obj, created = Contest.objects.get_or_create(
                contest_name = contest["contest_name"],
                city = contest["city"],
                defaults = {
                    "contest_slug": slugify_name(contest["contest_name"]) + "-" + slugify_name(contest["city"]),
                    "contest_url": contest["contest_url"]
                }
            )
            if not created:
                print "%s exists. Checking for updates..." % (contest["contest_name"])
                for x in contest:
                    if not contest[x] and getattr(obj,x):
                        print "SmartVoter's %s info for %s may have been deleted." % (x,contest["contest_name"])
                    elif contest[x] and getattr(obj,x) and contest[x] != getattr(obj,x):
                        setattr(obj,x,contest[x])
                        obj.change_date = timezone.now()
                        obj.save(update_fields=[x,'change_date'])
                        print "%s info for %s has been updated." % (x,contest["contest_name"] + " " + contest["city"])
                    elif contest[x] and not getattr(obj,x):
                        setattr(obj,x,contest[x])
                        obj.change_date = timezone.now()
                        obj.save(update_fields=[x,'change_date'])
                        print "%s info for %s has been updated." % (x,contest["contest_name"])

            elif created:
                print "%s created" % (contest["contest_name"])
        except ValueError, exception:
            #traceback.print_exc(file=sys.stdout)
            print "%s-%s" % (exception, contest["contest_name"])
            logger.debug("%s-%s" % (exception, contest["contest_name"]))

def fetch_measures(html):
    """
    Collects basic info on all LA County ballot measures for March 3.
    """
    found = 0
    rows = []
    for table in html.findAll('table'):
        tablesearch = table.findAll('table')
        
        for t in tablesearch:
            if t.tr.td.text == "Measures":
                found = 1
                mtable = t.findPrevious('table')
                measures = mtable.findAll('a')
                measures_total = len(measures)
                measure_rows = []

                #Set defaults to empty as needed
                measure_url = ""

                for x in range(measures_total):
                    if measures[x].has_key('href'):
                        if re.search(r'suggest',measures[x]['href']):
                            print str(measures[x]) + " ... BAD/EXCLUDE: This is not a ballot measure."
                        else:
                            measure_url = "http://www.smartvoter.org/2015/03/03/ca/la/meas/" + measures[x]['href']
                            row = parse_measure(measures[x],measure_url)
                            rows.append(row)
                    else:
                        row = parse_measure(measures[x],"")
                        rows.append(row)

    if found == 1:
        return rows
    else:
        print "No table found with info on ballot measures. Please check again."

def parse_measure(m,measure_url):
    titlestring = m.parent.text.encode("utf-8").replace("\n","")
    titlelist = re.split("--|\.",titlestring)
    measure_number = titlelist[0]
    measure_name = titlelist[1].replace(";","; ")
    city = titlelist[2].strip()
    measure_type = m.findNext('font', attrs={'size':'-1'}).text.encode("utf-8").replace("(","").replace(")","")
    description = m.findNext('dd').text.encode("utf-8").replace("\n"," ")

    # Create a row as dictionary and return it to the full dataset
    row = {
        'measure_number':measure_number,
        'measure_name':measure_name,
        'city':city,
        'measure_type':measure_type,
        'description':description,
        'measure_url':measure_url
        }
    return row

def add_or_update_measures(rows):
    for measure in rows:
        #measure["measure_number"] = measure["measure_number"].decode(encoding='UTF-8',errors='strict')
        try:
            obj, created = Measure.objects.get_or_create(
                measure_number = measure["measure_number"],
                city = measure["city"],
                defaults = {
                    "measure_slug": slugify_name(measure["measure_number"]),
                    "measure_name": measure["measure_name"],
                    "city": measure["city"],
                    "measure_type": measure["measure_type"],
                    "description": measure["description"],
                    "measure_url": measure["measure_url"]
                }
            )
            if not created:
                print "%s exists. Checking for updates..." % (measure["measure_number"])
                for x in measure:
                    if not measure[x] and getattr(obj,x):
                        print "SmartVoter's %s info for %s may have been deleted." % (x,measure["measure_number"])
                    elif measure[x] and getattr(obj,x) and measure[x] != getattr(obj,x):
                        setattr(obj,x,measure[x])
                        obj.change_date = timezone.now()
                        obj.save(update_fields=[x,'change_date'])
                        print "%s info for %s has been updated." % (x,measure["measure_number"])
                    elif measure[x] and not getattr(obj,x):
                        setattr(obj,x,measure[x])
                        obj.change_date = timezone.now()
                        obj.save(update_fields=[x,'change_date'])
                        print "%s info for %s has been updated." % (x,measure["measure_number"])

            elif created:
                print "%s created" % (measure["measure_number"])
        except ValueError, exception:
            #traceback.print_exc(file=sys.stdout)
            print "%s-%s" % (exception, measure["measure_number"])
            logger.debug("%s-%s" % (exception, measure["measure_number"]))

def fetch_all_candidates(html,ctype):
    """
    Collects contest name and candidate list for each, then fetches info on 
    each candidate.
    """
    races = html.findAll('a', href=re.compile('race/'))
    race_total = len(races)
    candidate_base_url = "http://www.smartvoter.org/2015/03/03/ca/la/"
    
    candidaterows = []
    contestrows = []
    
    for x in range(race_total):
        # Gather contest info
        contest_url = candidate_base_url + races[x]['href']
        candidate_rows = []
        contestlist = races[x].find('b').text.encode("utf-8").split(";")
        cityname = ""
        city = ""
        if ctype == "city.html":
            contest = contestlist[0].strip()
            city = contestlist[1].strip()
            if re.search(r'(Council Member|Councilmember)',contest):
                contest = "City Council"
        elif ctype == "school.html":
            cityname = re.search(r'^(\w+\s\w+)',contestlist[1].strip())
            if cityname:
                city = "City of " + cityname.group(1)
            contestdistrict = contestlist[1]
            contestseat = contestlist[0]
            if re.search(r'Los Angeles Community',contestdistrict):
                contest = "LA Community College Board of Trustees"
            elif re.search(r'Redondo Beach',contestdistrict):
                contest = "Redondo Beach School Board"
            elif re.search(r'Los Angeles Unified',contestdistrict):
                contest = "LAUSD School Board"
            else:
                contest = contestdistrict + " " + contestseat
        try:
            if contestlist[2]:
                contest = contest + contestlist[2]
        except:
            pass
        contestrows.append({
                'contest_name': contest,
                'city': city,
                'contest_url': contest_url
            })
        
        # Gather candidate info
        candidatelist = races[x].findNext('ul').findAll('li')
        for candidate in candidatelist:
            candidate_name = candidate.find('a').text.encode("utf-8")
            try:
                urlstring = candidate.find('a')['href']
                candidate_url = candidate_base_url + urlstring.encode(encoding='UTF-8',errors='strict')
            except:
                candidate_url = "none"
            candidate_row = fetch_candidate_info(candidate_name,candidate_url,contest,city)
            candidaterows.append(candidate_row)
    rowsbatch = {'contests':contestrows,'candidates':candidaterows}
    return rowsbatch

def fetch_candidate_info(candidate,target_url,contest,city):
    if target_url == "none":
        row = {
            'candidate':candidate,
            'contest':contest,
            'city':city,
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

def add_or_update_candidates(rows):
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
                    "candidate_url": candidate["candidate_url"]
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