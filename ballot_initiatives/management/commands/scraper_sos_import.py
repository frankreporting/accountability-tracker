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

logging.basicConfig(level=logging.DEBUG)

scraper_variables = {
	#'scrape' mode to pull data from SoS/AG sites; 'fileimport' mode to import from csv
	"mode": "scrape",
	"filepath":"scraper_managers/scraped/saved/sos-initiatives-import.csv",
}

class Command(BaseCommand):
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
		#logging.debug(os.path.realpath(os.path.dirname('scraper_managers/scraped/saved/sos-initiatives-import.csv')))
		if scraper_variables["mode"] == "fileimport":
			csvimport(scraper_variables["filepath"])
			self.stdout.write('Completed import.')
		elif scraper_variables["mode"] == "scrape":
			request_url_in("http://www.sos.ca.gov/elections/ballot-measures/")
			self.stdout.write('Completed scraping.')
		else:
			pass
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
	init_status = ["pending-signature-verification","failed-to-qualify","attorney-general-information","cleared-for-circulation"]
	rows = []
	
	for s in init_status:
		result = requests.get(base_url+s+'.htm')
		content = result.content
		soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
		data = parse_init_data_from_sos(soup,s)
		for item in data:
			rows.append(item)
	
	#Set key-value pairs
	keys = ['ag_id','id_note','sos_id','title','summary','full_text_link','proponent','email','phone','date_sum','status','date_qualified','date_failed','date_sample_due','date_raw_count_due','date_circulation_deadline','sigs_req','date_sample_update','sig_count_link','fiscal_impact_link','election','prop_num']

	importset = []
	for row in rows:
		importrow = {}
		for r in range(len(row)):
			importrow[keys[r]] = row[r]
		importset.append(importrow)
	for init in importset:
		check_if_exists_or_has_new_info(init)
	#write_data(headers,rows)


def parse_init_data_from_sos(html,init_status):
	data_block = html.find(id="centercontent")
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
			
			#Parse AG, Sec State initiative ID, Prop numbers and sig_count_link
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
	#Note: May not be able to handle status 'attorney-general-information'...lacked examples when coding
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
	try:
		query_init = Initiative.objects.get(sos_id=init["sos_id"])
		decide_whether_to_update(init,query_init)
	except:
		try:
			query_init = Initiative.objects.get(ag_id=init["ag_id"])
			decide_whether_to_update(init,query_init)
		except:
			create_and_save(init)
	#logging.debug(init)


def decide_whether_to_update(init,queried):
	if queried.status != init["status"]:
		update_existing(init,queried)
	elif queried.status == init["status"] and query_init.status == "pending-signature-verification":
		update_existing(init,queried)
	else:
		pass


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

	else:
		pass
		#need to include some kind of error reporting to handle this
		#possibly separate function for final decision to import, not importing if
		# there were no actual updates?


def create_and_save(init):
	#logging.debug(init["sos_id"] + " is a new record")
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
