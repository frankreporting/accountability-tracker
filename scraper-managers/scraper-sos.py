#!/usr/bin/python
"""
This script requires a command line argument.
You must tell it the status of the initiatives you want from the Secretary of State's website.
The format looks like this:
scraper-ag-inactive.py -s _______
Options are 'cleared','verifying','failed','pendingAG','qualified'
Ex. 'scraper-ag-inactive.py -s failed' will fetch initiatives that failed to qualify.
Default status is 'cleared'.

13 FIELDS NEED TO BE FILLED OR MADE EMPTY:
ag_id
id_note
sos_id
initiative_title
summary
proponent
email_adr
phone_num
summary_date
stat -- actually, this can be removed and "short_stat" can be rennamed "stat"
stat_date
sigs_req
doc_link
"""
import logging
import csv
import re
from optparse import OptionParser
import requests
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup

logging.basicConfig(level=logging.DEBUG)

parser = OptionParser()
parser.add_option("-s", "--status",action="store",type="string",dest="status",help="choose 'cleared','verifying','failed','pendingAG', or 'qualified'")
(options,args) = parser.parse_args()

if options.status == "verifying":
	init_status = "pending-signature-verification"
	short_stat = "Signature Verification"
elif options.status == "failed":
	init_status = "failed-to-qualify"
	short_stat = "Failed"
elif options.status == "pendingAG":
	init_status = "attorney-general-information"
	short_stat = "Attorney General's Office"
elif options.status == "qualified":
	init_status = "qualified-ballot-measures"
	short_stat = "Qualified"
elif options.status == "cleared":
	init_status = "cleared-for-circulation"
	short_stat = "Cleared to Circulate"
else:
	init_status = "cleared-for-circulation"
	short_stat = "Cleared to Circulate"

def request_url_in(target_url):
	result = requests.get(target_url)
	content = result.content
	soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
	parse_table_from(soup)

def parse_table_from(html):
	data_block = html.find(id="centercontent")
	if (init_status == "cleared-for-circulation" or init_status == "failed-to-qualify"):
		inits = data_block.findAll("p","prop-number-ag")
	else:
		inits = data_block.findAll("p",{"id": True})
	sums = data_block.findAll("p",{"class": "prop-text"})
	rows = []
	
	for i in range(len(inits)):
		#Check if it's a popular initiative or legislative referendum and set variables
		try:
			#If it has a class, then treat as popular initiative
			if inits[i]['class']:
				#Set initiative title
				initiative_title = data_block.findAll("p",{"class": re.compile("prop-title|text-strong")})[i].text.encode("utf-8")
				
				#Parse AG and Sec State initiative ID numbers
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
					#Note, for initiatives pending sig. verification, id_note will contain a link 
					#to the latest random sample update. Need to handle this in future.
					id_note = ""

				#Parse line with dates, signatures and initiative status
				dates = data_block.findAll("p",{"class": re.compile("prop-title|text-strong")})[i].findNext("p")
				date_block = dates.text.encode("utf-8").split("|")
				sum_date_block = date_block[0].split(":")
				summary_date = sum_date_block[1]
				if init_status == "qualified-ballot-measures":
					splitter = date_block[1].split(":")
					stat = splitter[0]
					stat_date = splitter[1].strip()
					sigs_req = date_block[2].split(":")[1].strip()
				elif len(date_block) == 2:
					splitter = date_block[1].split(":")
					stat = splitter[0]
					stat_date = splitter[1].strip()
					sigs_req = ""
				elif len(date_block) > 2:
					splitter = date_block[2].split(":")
					stat = splitter[0].strip()
					splitter2 = date_block[1].split(":")
					stat_date = splitter2[1].strip()
					sigs_req = splitter[1].replace(" ","")
				else:
					stat = ""
					stat_date = ""
					sigs_req = ""

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

				#Set summary
				summary = proponent_block.findNext("p").text.encode("utf-8")

				#Set extra fields to empty strings
				doc_link = ""
				
		#If it has no class, treat as a legislative referendum
		except KeyError:
			#Parse referendum ID number
			ag_id = inits[i]["id"]
			sos_id = ""
			id_note = "Referendum presented to voters by the legislature"
			
			#Set initiative title
			title_block = data_block.findAll("p",{"class": re.compile("prop-title|text-strong")})[i]
			initiative_title = title_block.text.encode("utf-8")
			doc_link = "http://www.sos.ca.gov" + title_block.a["href"]

			#Set summary
			summary = data_block.findAll("p",{"class": "text-emphasis"})[i].text.encode("utf-8")

			#Set extra fields to empty strings
			summary_date = ""
			stat = ""
			stat_date = ""
			sigs_req = ""
			proponent = ""
			email_adr = ""
			phone_num = ""
			
		#Add info to row cells and append to rows list according to initiative status
		rows.append([ag_id,id_note,sos_id,initiative_title.strip(),summary.strip(),doc_link,proponent,email_adr,phone_num,summary_date.strip(),short_stat,stat_date,sigs_req])
		
	
	#Set headers row based on initiative status
	if init_status == "failed-to-qualify":
		headers = ['ag_id','id_note','sos_id','title','summary','doc_link','proponent','email','phone','sum_date','status','fail_date','sig_req']
	elif init_status == "qualified-ballot-measures":
		headers = ['ag_id','id_note','sos_id','title','summary','doc_link','proponent','email','phone','sum_date','status','qualif_date','sig_req']
	else:
		headers = ['ag_id','id_note','sos_id','title','summary','doc_link','proponent','email','phone','sum_date','status','deadline','sig_req']
	
	write_data(headers,rows)

def write_data(headers,data):
	#ofile = open('scraped/sos-'+init_status+'-initiatives.csv',"wb")
	ofile = open('scraped/sos-initiatives.csv',"wb")
	writer = csv.writer(ofile,delimiter=',',quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow(headers)

	for row in data:
		writer.writerow(row)
	
	ofile.close()
		


if __name__ == '__main__':
	request_url_in('http://www.sos.ca.gov/elections/ballot-measures/'+init_status+'.htm')