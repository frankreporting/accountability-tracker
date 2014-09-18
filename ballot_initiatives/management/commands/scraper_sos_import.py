#!/usr/bin/python
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

scraper_variables = {
	#'scrape' mode to pull data from SoS/AG sites; 'fileimport' mode to import from csv
	"mode": "scrape",
	"filepath":"scraper_managers/scraped/saved/sos-initiatives-import.csv",
}

class Command(BaseCommand):
	#This block was intended to handle command line options to determine import method...
	# scrape vs. import from CSV. Couldn't get it working.
	"""
	option_list = BaseCommand.option_list + (
		make_option('--scrape', action='store', type='string', dest='scrape', help='Scrape data from Sec State/Attorney General sites. No args.'),
		make_option('--csv', action='store', type='string', dest='csv', help='Import data from csv file using <filepath> arg.'),
		)
	args = '<filepath>'

	help = 'Imports initiative data from Sec State and Attorney General sites. Use --scrape to pull \
		raw data or --csv to import from file'
	"""
	
	def handle(self, *args, **options):
		#logger.debug(os.path.realpath(os.path.dirname('scraper_managers/scraped/saved/sos-initiatives-import.csv')))
		if scraper_variables["mode"] == "fileimport":
			csvimport(scraper_variables["filepath"])
			self.stdout.write('Completed import.')
		elif scraper_variables["mode"] == "scrape":
			request_url_in("http://www.sos.ca.gov/elections/ballot-measures/")
			self.stdout.write('Completed scraping.')
		else:
			pass
		
		#The other part of the command line option block
		"""
		if options['scrape']:
			self.stdout.write('Completed')
			#request_url_in("http://www.sos.ca.gov/elections/ballot-measures/")
		elif options['csv']:
			try:
				csvimport(filepath)
			except:
				raise CommandError('File "%s" not found' % filepath)
		"""



### SCRAPER FUNCTIONS
def request_url_in(base_url):
	logger.debug("\n\n *** NEW IMPORT REQUEST MADE ON " + str(datetime.datetime.now()) + " ***\n\n")
	init_status = ["qualified-ballot-measures","pending-signature-verification","failed-to-qualify","attorney-general-information","cleared-for-circulation"]
	rows = []

	for s in init_status:
		result = requests.get(base_url+s+'.htm')
		content = result.content
		soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
		data = parse_based_on_status(soup,s)

		if data:
			for item in data:
				rows.append(item)
		else:
			logger.debug("No new initiatives or changes for status '" + s + ".'")
	
	#Set key-value pairs
	keys = ['ag_id','id_note','sos_id','title','summary','full_text_link','proponent','email','phone','date_sum','status','date_qualified','date_failed','date_sample_due','date_raw_count_due','date_circulation_deadline','sigs_req','date_sample_update','sig_count_link','fiscal_impact_link','election','prop_num']

	importset = []
	
	if rows:
		#Convert to list of dicts
		for row in rows:
			importrow = {}
			for r in range(len(row)):
				importrow[keys[r]] = row[r]
			importset.append(importrow)
		#Compare each dict to database and decide what to do
		for init in importset:
			check_if_exists_or_has_new_info(init)
			#pass
		#write_data(headers,rows)
	else:
		logger.debug("Nothing to import or update.")


def parse_based_on_status(html,init_status):
	data_block = html.find(id="centercontent")
	if init_status == "qualified-ballot-measures":
		rows = parse_qualified_init_data(data_block,init_status)
	else:
		parse_nonqualified_init_data(data_block,init_status)
		rows = []
	return rows

def parse_qualified_init_data(data_block,init_status):
	elections = data_block.findAll("h2")
	props = data_block.findAll("p",{"id": True})
	rows = []
	prop_ref = {}
	for p in range(len(props)):
		prop_ref[props[p]["id"]] = p
	#logger.debug(prop_ref)
	if len(elections) > 0:
		for e in range(len(elections)):
			#Figure out where election starts
			prop_start = elections[e].findNext("p",{"id": True})["id"]
			start = prop_ref[prop_start]
			
			#Figure out where election ends
			if e < len(elections)-1:
				prop_end = elections[e+1].findPrevious("p",{"id": True})["id"]
				end = prop_ref[prop_end]
			else:
				end = len(props)-1
			
			#Get details for each prop
			for x in props[start:end+1]:
				prop_id = x["id"]
				election = (" ").join(elections[e].text.split()[:2])
				prop_row = get_qualified_init_details(data_block,prop_id,election)
				#logger.debug(prop_row)
				rows.append(prop_row)
				
			#logger.debug(prop_start)
	else:
		logger.debug("No elections found. Double-check Secretary of State website at http://www.sos.ca.gov/elections/ballot-measures/qualified-ballot-measures.htm")
	#logger.debug(rows)
	return rows


def get_qualified_init_details(data,prop_id,election):
	#set defaults for now and revise later
	ag_id=""
	id_note=""
	sos_id=""
	initiative_title=""
	summary=""
	full_text_link=""
	proponent=""
	email_adr=""
	phone_num=""
	date_sum=""
	init_status="qualified-ballot-measures"
	date_qualified=""
	date_failed=""
	date_sample_due=""
	date_raw_count_due=""
	date_circulation_deadline=""
	sigs_req=""
	date_sample_update=""
	sig_count_link=""
	fiscal_impact_link=""
	prop_num=""
	
	#Parse prop id line based on all possible scenarios
	prop = data.find("p",{"id": prop_id})

	#For all inits/referrals before prop_num assigned...
	if not re.search("prop",prop["id"]):
		sos_id = prop["id"]
	if re.search("[0-9]{2}-[0-9]{4}",prop.text):
		ag_id = re.findall("[0-9]{2}-[0-9]{4}",prop.text)[0]

	#Special handling for props without title contained in html class "prop-title" or "text-strong"
	try:
		if prop.findNext("p")["class"] == "text-strong" or prop.findNext("p")["class"] == "prop-title":
			initiative_title_block = prop.findNext("p")
			initiative_title = initiative_title_block.text.encode("utf-8")
			if initiative_title_block.a:
				full_text_link = initiative_title_block.a["href"]
		elif prop.findNext("p").findNext("p")["class"] == "text-strong" or prop.findNext("p").findNext("p")["class"] == "prop-title":
			initiative_title_block = prop.findNext("p").findNext("p")
			initiative_title = initiative_title_block.text.encode("utf-8")
			if initiative_title_block.a:
				full_text_link = initiative_title_block.a["href"]
		else:
			pass
	except:
		pass
	if not initiative_title:
		initiative_title = prop.text.encode("utf-8")
		if prop.a:
			full_text_link = prop.a["href"]
	
	#For initiatives with prop_num...
	if re.search("Proposition",prop.text):
		prop_info = re.findall("Proposition [0-9]+",prop.text)[0]
		prop_num = re.findall("[0-9]+",prop_info)[0]
		if re.search("\*",prop.text):
			#Pull id_note note from tag 'text-emphasis' if '*' exists
			if data.find("span",{"class":"text-emphasis"}):
				asterisk_tag = data.find("span",{"class":"text-emphasis"}).text.encode("utf-8")
			if re.search("\*",asterisk_tag):
				id_note = asterisk_tag

	#For initiatives when they first qualify and no prop_num has been assigned...
	if re.search("^[0-9]{4}$",prop["id"]) and not re.search("Proposition",prop.text):
		sig_block = prop.a.text.encode("utf-8").split(" - ")
		sig_count_link = "http://www.sos.ca.gov" + prop.a["href"]
		date_sample_update = sig_block[1].strip()
		id_note = sig_block[0].strip()

		#Find and parse line with proponent info; extract phone number and email addresses if present
		if data.find("p",{"class":"prop-status"}):
			date_qual_block = data.find("p",{"class":"prop-status"})
			date_qualified = date_qual_block.text.encode("utf-8").split(":")[1].strip()
		
		if date_qual_block:
			proponent_block = date_qual_block.findNext("p")
		else:
			proponent_block = initiative_title_block.findNext("p")
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
		if data.find("p",{"class":"prop-text"}):
			summary_block = data.find("p",{"class":"prop-text"})
			summary = summary_block.text.encode("utf-8")

		if summary_block.a['href']:
			full_text_link = summary_block.a['href']
		
	#For legislative referrals when they first appear and no prop_num has been assigned...
	if not re.search("^[0-9]{4}$",prop["id"]) and not re.search("Proposition",prop.text):
		full_text_link = "http://www.sos.ca.gov" + prop.a["href"]

	#For legislative referrals after prop_num assigned...
	if re.search("Proposition",prop.text) and not re.search("prop",prop["id"]):
		prop_title_block = prop.text.encode("utf-8").split("\xe2\x80\x94")
		
		#Set proposition_type if there is one
		if data.find("p",{"class":"prop-type"}):
			proposition_type = data.find("p",{"class":"prop-type"}).text.encode("utf-8").strip()

		if len(prop_title_block) > 1:
			initiative_title = prop_title_block[1].strip() + " \xe2\x80\x94 " + initiative_title
	#logger.debug(prop_num + " | " + ag_id + " | " + sos_id)


	""" Qualified prop scraper code is tested up to this line with qual_test.py """

	#If ag_id isn't present, try fetching from AG site...
	#logger.debug(prop_num + ": ag_id is " + ag_id + " and date_qualified is " + date_qualified)
	if not ag_id and prop_num != "" or not date_qualified and prop_num != "":
		ag_details = attempt_ag_site_match(prop_num)
		if ag_details["match_status"] == 1:	
			ag_id = ag_details["ag_id"]
			date_qualified = ag_details["date_qualified"]
			logger.debug("Match found for Prop " + prop_num + ": " + ag_id + " | " + date_qualified)
		else:
			logger.debug("No matching records found for Prop " + prop_num + " on AG site.")
	#Notify of likely legislative referral or need for manual user match
	if not ag_id and not prop_num:
		logger.debug("No ag_id or prop_num for " + sos_id + " (" + initiative_title + "). Could be a legislative referral or there could be a problem. User needs to verify manually.")
		#Enter email alert info here

	return([ag_id,id_note,sos_id,initiative_title.strip(),summary.strip(),full_text_link,proponent,email_adr,phone_num,date_sum.strip(),init_status,date_qualified,date_failed,date_sample_due,date_raw_count_due,date_circulation_deadline,sigs_req,date_sample_update,sig_count_link,fiscal_impact_link,election,prop_num])

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
		rows.append([ag_id,id_note,sos_id,initiative_title.strip(),summary.strip(),full_text_link,proponent,email_adr,phone_num,date_sum.strip(),init_status,date_qualified,date_failed,date_sample_due,date_raw_count_due,date_circulation_deadline,sigs_req,date_sample_update,sig_count_link,fiscal_impact_link,election,prop_num])

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




### IMPORT FUNCTIONS
def csvimport(filepath):
	inits = read_data(filepath)
	for i in inits:
		check_if_exists_or_has_new_info(i)


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




### WRITE TO CSV: DEPRECATED BUT COULD BE REPURPOSED LATER
def write_data(headers,data):
	#ofile = open('scraped/sos-'+init_status+'-initiatives.csv',"wb")
	ofile = open('scraped/sos-initiatives.csv',"wb")
	writer = csv.writer(ofile,delimiter=',',quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow(headers)

	for row in data:
		writer.writerow(row)
	
	ofile.close()
