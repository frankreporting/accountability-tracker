#!/usr/bin/python
import logging
import csv
import re
import requests
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup

logging.basicConfig(level=logging.DEBUG)

def request_url_in(base_url):
	init_status = ["pending-signature-verification","failed-to-qualify","attorney-general-information","cleared-for-circulation"]
	rows = []
	
	for s in init_status:
		result = requests.get(base_url+s+'.htm')
		content = result.content
		soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
		data = parse_table_from(soup,s)
		for item in data:
			rows.append(item)
	
	#Set headers row based on initiative status
	headers = ['ag_id','id_note','sos_id','title','summary','full_text_link','proponent','email','phone','date_sum','status','date_qualified','date_failed','date_sample_due','date_raw_count_due','date_circulation_deadline','sigs_req','sig_count_link','fiscal_impact_link','election','prop_num']
	write_data(headers,rows)
	
def parse_table_from(html,init_status):
	data_block = html.find(id="centercontent")
	if (init_status == "cleared-for-circulation" or init_status == "failed-to-qualify"):
		inits = data_block.findAll("p","prop-number-ag")
	else:
		inits = data_block.findAll("p",{"id": True})
	sums = data_block.findAll("p",{"class": "prop-text"})
	rows = []
	
	for i in range(len(inits)):
		#This may need to be changed to a "try" statement or drop the "if" altogether
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
				date_sample_due = date_store['Random Sample Deadline']
			except:
				pass
			try:
				date_failed = date_store['Failed']
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
		rows.append([ag_id,id_note,sos_id,initiative_title.strip(),summary.strip(),full_text_link,proponent,email_adr,phone_num,date_sum.strip(),init_status,date_qualified,date_failed,date_sample_due,date_raw_count_due,date_circulation_deadline,sigs_req,sig_count_link,fiscal_impact_link,election,prop_num])

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

def write_data(headers,data):
	#ofile = open('scraped/sos-'+init_status+'-initiatives.csv',"wb")
	ofile = open('scraped/sos-initiatives.csv',"wb")
	writer = csv.writer(ofile,delimiter=',',quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow(headers)

	for row in data:
		writer.writerow(row)
	
	ofile.close()

if __name__ == '__main__':
	request_url_in('http://www.sos.ca.gov/elections/ballot-measures/')