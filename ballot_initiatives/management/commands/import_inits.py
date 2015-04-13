"""
NEXT UP! Need to refactor so ALL beautifulsoup parsing happens at the init_data level, and then
at the individual info parse level (title info, summary info, etc.), you're just parsing TEXT, so 
that they can be universal.
"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ballot_initiatives.models import Initiative
from scraper_managers.csv2pylist import read_data
import logging
import datetime
import csv
import os
import re
import requests
import pytz
from datetime import tzinfo
from pytz import timezone
from dateutil import parser
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup

#LOG_FILENAME = "scraper.log"
#logging.basicConfig(level=logging.DEBUG,filename=LOG_FILENAME)
logger = logging.getLogger('scraper_logger')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('scraper.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.debug("\n\n *** NEW IMPORT REQUEST MADE ON " + str(datetime.datetime.now()) + " ***\n\n")
        scrape_sos()
        #scrape_ag()
        self.stdout.write("\n\n *** END SCRAPE *** ")

class ScrapedInit(object):
    ag_id = ""
    sos_id = ""
    alt_id = ""
    id_note = ""
    title = ""
    summary = ""
    fiscal_impact = ""
    prop_num = ""
    proponent = ""
    proponent_search = ""
    email = ""
    phone = ""
    date_sum = ""
    date_sum_estimate = ""
    date_circulation_deadline = ""
    date_qualified = ""
    date_failed = ""
    date_sample_due = ""
    date_raw_count_due = ""
    date_sample_update = ""
    election = ""
    status = ""
    sigs_req = ""
    full_text_link = ""
    sig_count_link = ""
    sig_note = ""
    fiscal_impact_link = ""
    proposition_type = ""

    def __str__(self):
        return "<Scraped Initiative: ag_id = '%s' | sos_id = '%s' | alt_id = '%s' | id_note = '%s' | title = '%s' | summary = '%s' | fiscal_impact = '%s' | prop_num = '%s' | proponent = '%s' | proponent_search = '%s' | email = '%s' | phone = '%s' | date_sum = '%s' | date_sum_estimate = '%s' | date_circulation_deadline = '%s' | date_qualified = '%s' | date_failed = '%s' | date_sample_due = '%s' | date_raw_count_due = '%s' | date_sample_update = '%s' | election = '%s' | status = '%s' | sigs_req = '%s' | full_text_link = '%s' | sig_count_link = '%s' | sig_note = '%s' | fiscal_impact_link = '%s' | proposition_type = '%s'>" % (self.ag_id, self.sos_id, self.alt_id, self.id_note, self.title, self.summary, self.fiscal_impact, self.prop_num, self.proponent, self.proponent_search, self.email, self.phone, self.date_sum, self.date_sum_estimate, self.date_circulation_deadline, self.date_qualified, self.date_failed, self.date_sample_due, self.date_raw_count_due, self.date_sample_update, self.election, self.status, self.sigs_req, self.full_text_link, self.sig_count_link, self.sig_note, self.fiscal_impact_link, self.proposition_type)


### SHARED SCRAPER FUNCTIONS
def request_url_in(url,init_type,site):
    result = requests.get(url)
    if result.status_code != 200:
        logger.debug("ERROR: There was a problem trying to retrieve the page for initiatives '%s' on the %s." % (init_type,site))
    else:
        content = result.content
        soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
        return soup

### SCRAPE SEC STATE SITE
def scrape_sos():
    site = "Secretary of State's website"
    base_url = "http://www.sos.ca.gov/elections/ballot-measures/"
    sub_urls = [
        {
            "status":"qualified-ballot-measures", 
            "urlstr":"qualified-ballot-measures"
        },
        {
            "status":"pending-signature-verification", 
            "urlstr":"initiative-and-referendum-status/initiatives-and-referenda-pending-signature-verification"
        },
        {
            "status":"failed-to-qualify", 
            "urlstr":"initiative-and-referendum-status/failed-qualify"
        },
        {
            "status":"attorney-general-information",
            "urlstr":"attorney-general-information"
        },
        {
            "status":"cleared-for-circulation", 
            "urlstr":"initiative-and-referendum-status/initiatives-referenda-cleared-circulation"
        }
    ]
    for s in sub_urls:
        if s["status"] == "qualified-ballot-measures":
            soup = request_url_in(base_url + s["urlstr"],s["status"],site)
            parse_qualified_init_data(soup,s["status"])
        elif s["status"] == "attorney-general-information":
            pass
            #parse_pendingAG_init_data(soup,s)
        else:
            soup = request_url_in(base_url + s["urlstr"],s["status"],site)
            parse_nonqual_init_data(soup,s["status"])

def parse_qualified_init_data(html,init_status):
    data_block = html.find(id="mainCont")
    #elections = data_block.findAll("h2")
    props = data_block.findAll("p",{"id": True})
    docs = data_block.findAll("span",{"class": "fileTp"})
    
    # If more document links than props with IDs, then prop(s) likely haven't been 
    ## assigned an ID yet, so we'll instead locate props by locating the doc links
    if len(docs) > len(props):
        props = []
        for d in range(len(docs)):
            propitem = docs[d].findPrevious("p")
            props.append(propitem)

    # Get props
    for p in range(len(props)):
        id_block = props[p]
        prop = get_qualified_init_details(init_status,id_block)
        logger.debug(prop)

def parse_nonqual_init_data(html,init_status):
    data_block = html.find(id="mainCont")
    props = data_block.findAll("div",{"id": True})
    
    # Get props
    for p in props:
        id_block = p
        prop = get_nonqual_init_details(init_status,id_block)
        logger.debug(prop)


def parse_title_info(info):
    """
    captures initiative title and prop number depending on context; not tested on initiatives
    with prop number yet; id_note needs to be added if/when a prop on Sec State site uses it
    """
    title_data = {"title":"","type":"","prop_num":""}
    if re.search(r"(.*)\(PDF\)",info):
        clean = re.search(r"(.*)\(PDF\)",info)
        split = clean.group(1).split(". ")
    else:
        split = info.split(". ")
    lastitem = len(split) - 1
    if lastitem > 0 and re.search(r'Initiative|Amendment',split[lastitem]):
        title_data["type"] = split[lastitem]
        split.pop()
        title_data["title"] = '. '.join(split) + '.'
    elif lastitem == 0 and re.search(r'[Rr]{1}eferendum',split[0]):
        title_data["type"] = "Referendum"
        title_data["title"] = split[0]
    elif lastitem == 0 and not re.search(r'referendum',split[0]):
        title_data["title"] = split[0]
    elif re.search("Proposition",split[0]):
        prop_info = re.findall("Proposition [0-9]+",info)[0]
        title_data["prop_num"] = re.findall("[0-9]+",prop_info)[0]
    else:
        title_data["title"] = '. '.join(split) + '.'
    return title_data

def parse_date_info(info):
    """
    captures key dates and signature count info
    """
    date_data = {"date_qualified":"","date_circulation_deadline":""}
    info = info.split(":")
    if info[0] == "Qualified":
        date_data["date_qualified"] = info[1]
    return date_data

def parse_proponent_info(info):
    """
    captures proponent name(s), plus email and phone number where provided
    """
    pro_data = {"email":"","phone":"","proponent":"","proponent_search":""}
    try:
        email_test = info.findAll("a")
    except:
        email_test = False
    if email_test:
        pro_data["email"] = email_test[0].text.encode("utf-8")
        proponent_str = info.text.encode("utf-8").replace(pro_data["email"],"").strip()
    else:
        proponent_str = info
    phone_test = re.search(r'(\([0-9]{3}\)\s?[0-9]{3}\-[0-9]{4})',proponent_str)
    if phone_test:
        pro_data["phone"] = phone_test.group(1)
        proponent_str2 = proponent_str.replace(pro_data["phone"],"").strip()
    else:
        proponent_str2 = proponent_str
    pro_data["proponent"] = proponent_str2
    
    # Separate multiple proponent names to enable searching by name later
    proponents = []
    co_test = re.search(r'[Cc]/[Oo]',proponent_str2)
    comma_test = re.search(',',proponent_str2)
    and_test = re.search(r' and ',proponent_str2)
    if co_test:
        names = re.compile(r'[Cc]/[Oo]').split(proponent_str2)
        for name in names:
            proponents.append(name.strip())
    else:
        proponents.append(proponent_str2)
    for name in proponents:
        if comma_test:
            names = name.split(",")
            for n in names:
                proponents.append(n.strip())
    for name in proponents:
        if and_test:
            names = name.split(" and ")
            for n in names:
                proponents.append(n.strip())
    deletions = []
    for p in range(len(proponents)):
        if re.match(r'[Jj]r[\.]?|[Ss]r[\.]?|^[Ii]+$',proponents[p]):
            #suffix = proponents.pop(p)
            proponents[p-1] += ", " + proponents[p]
            deletions.append(p)
    for d in deletions:
        del proponents[d]
    first = True
    for p in proponents:
        if first:
            pro_data["proponent_search"] = p
            first = False
        else:
            pro_data["proponent_search"] += "|" + p
    return pro_data

def parse_summary_info(info):
    """
    captures summary and link to full text, plus brief fiscal impact statement if present
    """
    sum_data = {"summary":"","full_text_link":"","fiscal_impact":""}
    try:
        sum_data["full_text_link"] = info.a["href"]
    except:
        pass
    try:
        sum_block = info.text.encode("utf-8")
    except:
        sum_block = info
    fiscal_test = re.search('Summary of estimate by Legislative Analyst',sum_block)
    if fiscal_test:
        parse_summary = re.search(r'^(.*)(Summary of estimate by Legislative Analyst.*$)',sum_block)
        summary = parse_summary.group(1).strip()
        sum_data["fiscal_impact"] = remove_summary_parentheticals(parse_summary.group(2))
    else:
        summary = remove_summary_parentheticals(sum_block)
    sum_data["summary"] = summary

    ### WHERE I LEFT OFF: Next need to clean up summary by removing (Full Text) etc. and populate sum_data
    #logger.debug(summary)
    return sum_data

def remove_summary_parentheticals(text):
    ag_id_remover = re.search(r'(.*)(\([0-9]{2}\-[0-9]{4}.*\))',text)
    try:
        if ag_id_remover.group(2):
            text = ag_id_remover.group(1)
    except:
        pass
    full_text_link_remover = re.search(r'(.*)(\(Full Text\))',text)
    try:
        if full_text_link_remover.group(2):
            text = full_text_link_remover.group(1)
    except:
        pass
    return text.strip()

def parse_id_info(sos_id,info):
    id_data = {"sos_id":"", "ag_id":"", "sig_count_link":"", "date_sample_update":"", "sig_note":""}
    try:
        id_data["sos_id"] = sos_id
    except:
        pass
    agmatch = re.search(r'[0-9]{2}\-[0-9]{4}',info.text)
    if agmatch:
        try:
            id_data["ag_id"] = agmatch.group(0)
        except:
            pass
    try:
        if info.a:
            id_data["sig_count_link"] = info.a["href"]
            sig_block = info.a.text.encode("utf-8").split("-")
            id_data["sig_note"] = sig_block[0].strip()
            sample_date = re.search(r'([0-9]{1,2}/[0-9]{1,2}/[0-9]+)',sig_block[1].strip())
            id_data["date_sample_update"] = sample_date.group(1)
            # May need to adjust later to assess type of date based on language...sample update, or sample due date, etc.?
    except:
        pass
    return id_data

def get_init_by_id():
    pass

def get_init_by_alt_id():
    pass

def get_init_without_id():
    pass

def get_nonqual_init_details(init_status,id_block):
    prop = ScrapedInit()
    prop.status = init_status

    prop_details = [re.sub(r'<.*?>','',x) for x in str(id_block.findNext("p")).split("<br />")]
    try:
        pidmatch = re.match(r'[0-9]{4}',prop_details[0])
        if pidmatch:
            id_info = parse_id_info(pidmatch.group(),id_block)
        else:
            id_info = parse_id_info("",)
    except:
        pass


    ## STORE DATA
    # Store id info
    try:
        prop.sos_id = id_info["sos_id"]
        prop.ag_id = id_info["ag_id"]
        prop.sig_count_link = id_info["sig_count_link"]
        prop.sig_note = id_info["sig_note"]
        prop.date_sample_update = id_info["date_sample_update"]
    except:
        pass

    return prop

def get_qualified_init_details(init_status,id_block):
    prop = ScrapedInit()
    prop.status = init_status
    election_text = re.match(r'^\w+\s[0-9]+',id_block.findPrevious("h2").text)
    try:
        prop.election = election_text.group()
    except:
        pass

    # Determine type of initiative we're dealing with and handle remaining info accordingly...
    try:
        ## PROPS THAT HAVE CLEAR SOS_ID
        pid = id_block["id"]
        pidmatch = re.match(r'[0-9]{4}',pid)
        if pidmatch:
            try: 
                id_info = parse_id_info(pidmatch.group(),id_block)
            except:
                pass
            try:
                title_info = parse_title_info(id_block.findNext("p").text.encode("utf-8"))
            except:
                pass
            try:
                date_info = parse_date_info(id_block.findNext("p").findNext("p").text.encode("utf-8"))
            except:
                pass
            try:
                pro_info = parse_proponent_info(id_block.findNext("p").findNext("p").findNext("p").text.encode("utf-8"))
            except:
                pass
            try:
                sum_info = parse_summary_info(id_block.findNext("p").findNext("p").findNext("p").findNext("p"))
                prop.full_text_link = sum_info["full_text_link"]
            except:
                pass

        ## PROPS THAT DON'T HAVE CLEAR SOS_ID BUT HTML TAG HAS AN ID WE CAN USE
        else:
            try:
                prop.alt_id = pid
            except:
                pass
            try:
                if id_block.a:
                    prop.full_text_link = id_block.a["href"]
            except:
                pass
            try:
                title_info = parse_title_info(id_block.a.text.encode("utf-8"))
            except:
                pass

    ## PROPS THAT HAVE NO ID AND HTML TAG IS UNSTYLED
    except:
        pmatch = re.match(r'^\w+\s[0-9]+',id_block.text)
        try:
            prop.alt_id = pmatch.group()
        except:
            pass
        try:
            if id_block.a:
                prop.full_text_link = id_block.a["href"]
        except:
            pass
        try:
            title_info = parse_title_info(id_block.a.text.encode("utf-8"))
        except:
            pass

    ## STORE REMAINING INFO
    
    # Store id info
    try:
        prop.sos_id = id_info["sos_id"]
        prop.ag_id = id_info["ag_id"]
        prop.sig_count_link = id_info["sig_count_link"]
        prop.sig_note = id_info["sig_note"]
        prop.date_sample_update = id_info["date_sample_update"]
    except:
        pass

    # Store title info
    try:
        prop.title = title_info["title"]
        prop.proposition_type = title_info["type"]
        prop.prop_num = title_info["prop_num"]
    except:
        pass
    
    # Store date info
    try:
        prop.date_qualified = date_info["date_qualified"]
        prop.date_circulation_deadline = date_info["date_circulation_deadline"]
    except:
        pass
    
    # Store proponent block info
    try:
        prop.proponent = pro_info["proponent"]
        prop.proponent_search = pro_info["proponent_search"]
        prop.email = pro_info["email"]
        prop.phone = pro_info["phone"]
    except:
        pass

    # Store summary block info
    try:
        prop.summary = sum_info["summary"]
        prop.fiscal_impact = sum_info["fiscal_impact"]
    except:
        pass

    return prop








### AG FUNCTIONS
def scrape_ag():
    logger.debug("Scraping the Attorney General site now!")
    new_ag_init = Initiative()
    new_ag_init.ag_id = "This is you ag_id"
    logger.debug(new_ag_init.ag_id)
    logger.debug(new_ag_init.id_note)


### CHECK AGAINST DATABASE

def check_if_exists_or_has_new_info():
    pass

def decide_whether_to_update():
    pass

def update_existing():
    pass

def create_and_save():
    pass


### OLD FUNCTIONS
def parse_pendingAG_init_data(data_block,init_status):
    rows = []
    table = data_block.findAll("table")
    #If more than one table exists, we have a problem...
    if len(table) > 1:
        logger.debug("Problem: More than one table listed. Please double-check SoS site.")

    #If table doesn't exist...
    elif not table:
        logger.debug("No new initiatives pending Attorney General review.")

    #If table exists, scrape initiatives...
    else:
        inits = []
        rows = table[0].findAll("tr")
        for r in rows:
            if r.find("td"):
                inits.append(r)

        #Process initiative data
        for i in inits:
            init_data = i.findAll("td")
            ag_id_block = init_data[0].text.encode("utf-8").split()
            ag_id = ag_id_block[0].strip()
            date_sum_estimate = ag_id_block[len(ag_id_block)-1].strip()         
            full_text_link = init_data[1].a["href"]
            initiative_title = init_data[1].text.encode("utf-8").strip().replace('"','')
            proponent = init_data[2].text.encode("utf-8").strip()
            return_rows.append([ag_id,id_note,sos_id,initiative_title,summary,full_text_link,proponent,email_adr,phone_num,date_sum,date_sum_estimate,init_status,date_qualified,date_failed,date_sample_due,date_raw_count_due,date_circulation_deadline,sigs_req,date_sample_update,sig_count_link,fiscal_impact_link,election,prop_num])


def attempt_ag_site_match(pnum):
    ag_qualified_props = []
    if not ag_qualified_props:  
        #Load most recent qualified initiatives into var ag_qualified_props
        target_url = "http://oag.ca.gov/initiatives/qualified-for-ballot"
        result = requests.get(target_url)
        content = result.content
        soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)  
        

        data_table = soup.find('table')
        data_rows = data_table.findAll('tr')[1:]

        for row in data_rows:
            data_cells = row.findAll('td')
            initiative_details = data_cells[1]
            anchors = initiative_details.findAll('a')[0:]
            initiative_title = initiative_details.contents[2]
            initiative_id_link = data_cells[0].a["href"]
            initiative_id = data_cells[0].text.encode("utf-8")
            #date_link = anchors[0]['href']
            date_block = anchors[0].find('span')['content'].split("-")
            date_sum = date_block[1] + "/" + date_block[2][0:2] + "/" + date_block[0]
            qual_date_block = initiative_details.find('strong',text=re.compile("Qualified")).findNext('span','date-display-single')['content'].split("-")
            date_qualified = qual_date_block[1] + "/" + qual_date_block[2][0:2] + "/" + qual_date_block[0]
            ag_id = data_cells[0].text.encode("utf-8").strip()
            #logger.debug(pnum + ": " + ag_id)
            detail_soup = data_cells[1].text.encode("utf-8")
            if re.search(r"Proposition Number.*[0-9]+.*$",detail_soup):
                prop_full = re.findall(r"Proposition Number.*[0-9]+.*$",detail_soup)[0]
                prop_num = prop_full.split(":")[1].strip()
            else:
                prop_num = ""
            #if len(anchors) > 0:
                #fiscal_impact = anchors[1]['href']
            fiscal_impact = ""
            proponent = initiative_details.contents[9]
            
            ag_qualified_props.append({"initiative_id":initiative_id,"initiative_title":initiative_title.strip(),"initiative_id_link":initiative_id_link,"proponent":proponent.strip(),"date_sum":date_sum,"date_qualified":date_qualified,"fiscal_impact":fiscal_impact,"prop_num":prop_num,"ag_id":ag_id})
                        
    #Attempt to match prop_num to an ag_id
    #logger.debug(ag_qualified_props)
    prop_index = dict((p['prop_num'], i) for i, p in enumerate(ag_qualified_props))
    try:
        index = prop_index.get(pnum)
        ag_id = ag_qualified_props[index]["ag_id"]
        date_qualified = ag_qualified_props[index]["date_qualified"]
        return {"ag_id":ag_id,"date_qualified":date_qualified,"match_status":1}
    except:
        return {"ag_id":"","date_qualified":"","match_status":0}

    
    
def parse_nonqualified_init_data(data_block,init_status):
    if (init_status == "cleared-for-circulation" or init_status == "failed-to-qualify"):
        inits = data_block.findAll("p","prop-number-ag")
    else:
        inits = data_block.findAll("p",{"id": True})
    sums = data_block.findAll("p",{"class": "prop-text"})
    rows = []
    
    for i in range(len(inits)):
        #This may need to be changed to a "try" statement or drop the "if" altogether
        #  because I believe "class" would always be present for non-qualified initiatives
        if inits[i]['class']:
            #Set initiative title
            initiative_title = data_block.findAll("p",{"class": re.compile("prop-title|text-strong")})[i].text.encode("utf-8")
            
            #Parse AG ID, Sec State initiative ID and sig_count_link
            initiative_id_block = inits[i].text.encode("utf-8").split("(")
            sos_id = initiative_id_block[0].replace(".","").strip()
            ag = initiative_id_block[1].replace(")","").split()
            ag_id = ag[0].replace(",","")
            
            if ag > 1:
                items = []
                for item in ag[1:]:
                    item.replace(" ","")
                    items.append(item)
                id_note = " ".join(items).replace("-","")
            else:
                id_note = ""
            if init_status == "pending-signature-verification":
                sig_count_link = "http://www.sos.ca.gov" + inits[i].a["href"]
                date_sample_update = inits[i].a.text.encode("utf-8").split(" - ")[1].strip()
            else:
                sig_count_link = ""
            election = ""
            prop_num = ""

            #Get fiscal impact report link
            fiscal_impact_link = req_fiscal_impact(ag_id,init_status)

            #Set dates and sigs_req fields to empty first
            date_sum = ""
            date_sum_estimate= ""
            date_qualified = ""
            date_failed = ""
            date_sample_due = ""
            date_sample_update = ""
            date_raw_count_due = ""
            date_circulation_deadline = ""
            sigs_req = ""

            #Parse line with dates, signatures and initiative status, populate as able
            dates = data_block.findAll("p",{"class": re.compile("prop-title|text-strong")})[i].findNext("p")
            date_block = dates.text.encode("utf-8").split("|")
            sum_date_block = date_block[0].split(":")

            date_store = {}
            for each in date_block:
                value_keys = each.split(":")
                date_store[value_keys[0].strip()] = value_keys[1].strip()
            # Check to see if this can be refactored to use 'if date_store.has_key('Summary Date'), etc'
            try:
                date_circulation_deadline = date_store['Circulation Deadline']
            except:
                pass
            try: 
                date_sum = date_store['Summary Date']
            except:
                pass
            try:
                sigs_req = date_store['Signatures Required']
            except:
                pass
            try:
                date_raw_count_due = date_store['Raw Count Deadline']
            except:
                pass
            try:
                date_failed = date_store['Failed']
            except:
                pass
            #Handle signature check updates
            try:
                date_sample_due = date_store['Random Sample Deadline']
                #May need to add a few try/excepts in case this is sometimes listed as 
                #  something else, i.e. "Final Full Check Due"
            except:
                pass

            #Find and parse line with proponent info; extract phone number and email addresses if present
            proponent_block = dates.findNext("p")
            email_test = proponent_block.findAll("a")
            if email_test:
                email_adr = email_test[0].text.encode("utf-8")
            else:
                email_adr = ""
            proponent_str = proponent_block.text.encode("utf-8").replace(email_adr,"").replace("Proponent:","").strip()
            phone_test = re.findall("\\([0-9]{3}\\)\\s?[0-9]{3}-[0-9]{4}",proponent_str)
            if phone_test:
                first = True
                for item in phone_test:
                    if first:
                        first = False
                        phone_num = item
                    else:
                        phone_num = "\n" + item
            else:
                phone_num = ""
            proponent = proponent_str.replace(phone_num,"").strip()

            #Set summary and full text link
            summary = proponent_block.findNext("p").text.encode("utf-8")

            if proponent_block.findNext("p").a['href']:
                full_text_link = proponent_block.findNext("p").a['href']
            else:
                full_text_link = ""
                
        #Add info to row cells and append to rows list according to initiative status
        rows.append([ag_id,id_note,sos_id,initiative_title.strip(),summary.strip(),full_text_link,proponent,email_adr,phone_num,date_sum.strip(),date_sum_estimate,init_status,date_qualified,date_failed,date_sample_due,date_raw_count_due,date_circulation_deadline,sigs_req,date_sample_update,sig_count_link,fiscal_impact_link,election,prop_num])

    return rows


def req_fiscal_impact(ag_id,init_status):
    year = ag_id.split("-")[0]
    if init_status == "failed-to-qualify":
        target_url = "http://oag.ca.gov/initiatives/inactive-measures?field_initiative_date_value%5Bvalue%5D%5Byear%5D=20" + year
    else:
        target_url = "http://oag.ca.gov/initiatives/active-measures"
    #Note: May not be ready to handle status 'attorney-general-information'...lacked examples when coding
    result = requests.get(target_url)
    content = result.content
    soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)  
    link = parse_ag_data(soup,ag_id)
    return link


def parse_ag_data(html,ag_id):
    data_table = html.find('table')
    data_rows = data_table.findAll('tr')[1:]

    rows = []
    for row in data_rows:
        data_cells = row.findAll('td')
        initiative_details = data_cells[1]
        anchors = initiative_details.findAll('a')[0:]
        initiative_id = data_cells[0].text.encode("utf-8")      
        if initiative_id == ag_id:
            fiscal_impact = anchors[1]['href']
            return fiscal_impact




### Functions I might need later...
def convert_time_to_nicey_format(date_time_parse):
    """
    Copied from Chris Keller's Fire Tracker scraper...
    based on http://stackoverflow.com/questions/17193228/python-twitter-api-tweet-timestamp-convert-from-utc-to-est
    """
    date_time_parse = date_time_parse.strip("&nbsp;")
    utc = timezone("UTC")
    pacific = pytz.timezone("US/Pacific")
    date_time_parse = parser.parse(date_time_parse)
    pacificizd_date_time_parse = pacific.localize(date_time_parse)
    return pacificizd_date_time_parse


def check_if_exists_or_has_new_info(init):
    #Need to add another nested layer to try matching prop_num if sos_id and ag_id fail
    query_init = Initiative.objects.filter(sos_id__exact=init["sos_id"]).exclude(sos_id__exact="")
    if len(query_init) == 0:
        query_init = Initiative.objects.filter(ag_id__exact=init["ag_id"]).exclude(ag_id__exact="")
        if len(query_init) == 0:
            query_init = Initiative.objects.filter(prop_num__exact=init["prop_num"]).exclude(prop_num__exact="")
            if len(query_init) == 0:
                #logger.debug(init["ag_id"] + " or " + init["sos_id"] + " is not in the database. Need to add.")
                create_and_save(init)
            elif len(query_init) > 1:
                logger.debug("There's a duplicate of Proposition " + init["prop_num"] + " in the database.")
            else:
                logger.debug("Matched based on prop_num")
                decide_whether_to_update(init,query_init[0])
        elif len(query_init) > 1:
            logger.debug("There's a duplicate of " + init["ag_id"] + " in the database.")
        else:
            logger.debug("Matched based on ag_id")
            decide_whether_to_update(init,query_init[0])
    elif len(query_init) > 1:
        logger.debug("There's a duplicate of " + init["sos_id"] + "|" + init["ag_id"] + " in the database.")
    else:
        logger.debug("Matched based on sos_id")
        decide_whether_to_update(init,query_init[0])


def decide_whether_to_update(init,queried):
    #logger.debug("IMPORT RECORD:" + init["sos_id"] + " | " + init["ag_id"] + " | " + init["prop_num"])
    #logger.debug("DATABASE MATCH:" + queried.sos_id + " | " + queried.ag_id + " | " + queried.prop_num)
    if queried.status != init["status"]:
        logger.debug(queried.sos_id + "/" + queried.ag_id + " has a status update. Status in database is " + queried.status + " but imported status is " + init["status"])
        update_existing(init,queried)
        #logger.debug(init)
        #logger.debug(queried)
    elif queried.status == "pending-signature-verification":
        logger.debug(queried.sos_id + "/" + queried.ag_id + " is pending signature verification. Need to check for sample updates.")
        update_existing(init,queried)
        #logger.debug(init)
        #logger.debug(queried)
    elif queried.status == "qualified-ballot-measures":
        logger.debug(queried.sos_id + "/" + queried.ag_id + " has qualified. Need to check for prop_num or other changes.")
        update_existing(init,queried)
    else:
        #pass
        logger.debug(queried.ag_id + "'s status has not changed. No need to update.")


def update_existing(init,queried):
    #Updates for all, regardless of status
    if queried.status != init["status"]:
        queried.status = init["status"]
    
    #Updates based on status
    if init["status"] == "pending-signature-verification":
        if queried.sig_count_link != init["sig_count_link"]:
            queried.sig_count_link = init["sig_count_link"]
        if queried.id_note != init["id_note"]:
            queried.id_note = init["id_note"]
        if init.has_key("date_sample_update"):
            if init["date_sample_update"]:
                date_sample_update = convert_time_to_nicey_format(init["date_sample_update"])
                if queried.date_sample_update != date_sample_update:
                    queried.date_sample_update = date_sample_update
        if init.has_key("date_raw_count_due"):
            if init["date_raw_count_due"]:
                date_raw_count_due = convert_time_to_nicey_format(init["date_raw_count_due"])
                if queried.date_raw_count_due != date_raw_count_due:
                    queried.date_raw_count_due = date_raw_count_due
        queried.save()

    elif init["status"] == "failed-to-qualify":
        if init.has_key("date_failed"):
            if init["date_failed"]:
                date_failed = convert_time_to_nicey_format(init["date_failed"])
                if queried.date_failed != date_failed:
                    queried.date_failed = date_failed
        queried.save()
    
    elif init["status"] == "cleared-for-circulation" or init["status"] == "attorney-general-information":
        #Check most fields
        #Handle dates as special case
        if init.has_key("date_circulation_deadline"):
            if init["date_circulation_deadline"]:
                date_circulation_deadline = convert_time_to_nicey_format(init["date_circulation_deadline"])
                if queried.date_circulation_deadline != date_circulation_deadline:
                    queried.date_circulation_deadline = date_circulation_deadline
        if init.has_key("date_sum"):
            if init["date_sum"]:
                date_sum = convert_time_to_nicey_format(init["date_sum"])
                if queried.date_sum != date_sum:
                    queried.date_sum = date_sum
        #Check remaining fields
        if queried.ag_id != init["ag_id"]:
            queried.ag_id = init["ag_id"]
        if queried.id_note != init["id_note"]:
            queried.id_note = init["id_note"]
        if queried.sos_id != init["sos_id"]:
            queried.sos_id = init["sos_id"]
        if queried.title != init["title"]:
            queried.title = init["title"]
        if queried.summary != init["summary"]:
            queried.summary = init["summary"]
        if queried.full_text_link != init["full_text_link"]:
            queried.full_text_link = init["full_text_link"]
        if queried.proponent != init["proponent"]:
            queried.proponent = init["proponent"]
        if queried.email != init["email"]:
            queried.email = init["email"]
        if queried.phone != init["phone"]:
            queried.phone = init["phone"]
        if queried.sigs_req != init["sigs_req"]:
            queried.sigs_req = init["sigs_req"]
        if queried.fiscal_impact_link != init["fiscal_impact_link"]:
            queried.fiscal_impact_link = init["fiscal_impact_link"]
        queried.save()

    elif init["status"] == "qualified-ballot-measures":
        if queried.sig_count_link != init["sig_count_link"]:
            queried.sig_count_link = init["sig_count_link"]
        if queried.id_note != init["id_note"]:
            queried.id_note = init["id_note"]
        if init.has_key("date_sample_update"):
            if init["date_sample_update"]:
                date_sample_update = convert_time_to_nicey_format(init["date_sample_update"])
                if queried.date_sample_update != date_sample_update:
                    queried.date_sample_update = date_sample_update
        if init.has_key("date_qualified"):
            if init["date_qualified"]:
                date_qualified = convert_time_to_nicey_format(init["date_qualified"])
                if queried.date_qualified != date_qualified:
                    queried.date_qualified = date_qualified
        if queried.full_text_link != init["full_text_link"]:
            queried.full_text_link = init["full_text_link"]
        if queried.election != init["election"]:
            queried.election = init["election"]
        if queried.status != init["status"]:
            queried.status = init["status"]
        if queried.prop_num != init["prop_num"]:
            queried.prop_num = init["prop_num"]
        queried.save()

    else:
        pass
        #need to include some kind of error reporting to handle this
        #possibly separate function for final decision to import, not importing if
        # there were no actual updates?


def create_and_save(init):
    #logger.debug(init["sos_id"] + " is a new record")
    newrecord = Initiative()
    if init.has_key("ag_id"):
        newrecord.ag_id = init["ag_id"]
    if init.has_key("id_note"):
        newrecord.id_note = init["id_note"]
    if init.has_key("sos_id"):
        newrecord.sos_id = init["sos_id"]
    if init.has_key("title"):
        newrecord.title = init["title"]
    if init.has_key("summary"):
        newrecord.summary = init["summary"]
    if init.has_key("date_sum"):
        if init["date_sum"]:
            newrecord.date_sum = convert_time_to_nicey_format(init["date_sum"])
    if init.has_key("date_sum_estimate"):
        if init["date_sum_estimate"]:
            newrecord.date_sum_estimate = convert_time_to_nicey_format(init["date_sum_estimate"])
    if init.has_key("full_text_link"):
        newrecord.full_text_link = init["full_text_link"]
    if init.has_key("proponent"):
        newrecord.proponent = init["proponent"]
    if init.has_key("email"):
        newrecord.email = init["email"]
    if init.has_key("phone"):
        newrecord.phone = init["phone"]
    if init.has_key("status"):
        newrecord.status = init["status"]
    if init.has_key("date_qualified"):
        if init["date_qualified"]:
            newrecord.date_qualified = convert_time_to_nicey_format(init["date_qualified"])
    if init.has_key("date_failed"):
        if init["date_failed"]:
            newrecord.date_failed = convert_time_to_nicey_format(init["date_failed"])
    if init.has_key("date_sample_due"):
        if init["date_sample_due"]:
            newrecord.date_sample_due = convert_time_to_nicey_format(init["date_sample_due"])
    if init.has_key("date_raw_count_due"):
        if init["date_raw_count_due"]:
            newrecord.date_raw_count_due = convert_time_to_nicey_format(init["date_raw_count_due"])
    if init.has_key("date_circulation_deadline"):
        if init["date_circulation_deadline"]:
            newrecord.date_circulation_deadline = convert_time_to_nicey_format(init["date_circulation_deadline"])
    if init.has_key("sigs_req"):
        newrecord.sigs_req = init["sigs_req"]
    if init.has_key("sig_count_link"):
        newrecord.sig_count_link = init["sig_count_link"]
    if init.has_key("date_sample_update"):
        if init["date_sample_update"]:
            newrecord.date_sample_update = convert_time_to_nicey_format(init["date_sample_update"])
    if init.has_key("fiscal_impact_link"):
        newrecord.fiscal_impact_link = init["fiscal_impact_link"]
    if init.has_key("election"):
        newrecord.election = init["election"]
    if init.has_key("prop_num"):
        newrecord.prop_num = init["prop_num"]
    newrecord.save()