#!/usr/bin/python
"""
This script will fetch initiatives from every year in the UC Hastings College of Law's
archive of California ballot initiatives and propositions.

NEXT STEPS:
- Debug these URLs:
	http://repository.uchastings.edu/ca_ballot_inits/1573

"""

import logging
import csv
import re
import requests
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup

logging.basicConfig(level=logging.DEBUG)

def request_url_in(target_url):
	result = requests.get(target_url)
	content = result.content
	soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
	fetch_all_pages(soup)

def fetch_all_pages(html):
	page_total = int(html.find("span","counter").findAll("strong")[1].text.encode("utf-8"))
	first = 1
	base_url = "http://repository.uchastings.edu/ca_ballot_inits/"
	#test_url = "http://repository.uchastings.edu/ca_ballot_inits/1573"
	#fetch_page(base_url)
	
	#test_single_page(test_url)
	

	
	#For testing, use base_url. To enable looping thru all pages, use code below:

	for x in range(page_total):
		page = x + 1
		if page == first:
			page_url = base_url
		else:
			page_url = base_url + "index." + str(page) + ".html"
		fetch_page(page_url)
	
"""
def test_single_page(target_url):
	rows = []
	row = get_init(target_url)
	rows.append(row)
	
	headers = ['ag_id','id_note','sos_id','init_title','summary','doc_link','proponent','email','phone','submit_date','doc_type','status','citation']
	write_data(headers,rows)	
"""

def fetch_page(target_url):
	result = requests.get(target_url)
	content = result.content
	soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
	fetch_inits_from(soup)

def fetch_inits_from(html):
	inits = html.findAll("p","article-listing")
	rows = []
	"""
	init_url = inits[12].a["href"]
	row = get_init(init_url)
	rows.append(row)
	"""
	for i in range(len(inits)):
		init_url = inits[i].a["href"]
		row = get_init(init_url)
		rows.append(row)
	
	headers = ['ag_id','id_note','sos_id','init_title','summary','doc_link','proponent','email','phone','submit_date','doc_type','status','citation']
	write_data(headers,rows)

def get_init(target_url):
	result = requests.get(target_url)
	content = result.content
	soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
	try:
		return parse_fields_from(soup)
	except:
		raw_input("PRESS ENTER TO CONTINUE.")

def parse_fields_from(html):
	data_block = html.find(id="alpha")
	data_fields = data_block.findAll('h4')
	ag_id = ""
	id_note = ""
	sos_id = ""
	citation = ""
	summary = ""
	initiative_title = ""
	proponent = ""
	email_adr = ""
	phone_num = ""
	summary_date = ""
	stat = ""
	doc_link = ""
	doc_type = ""

	for item in data_fields:
		header = item.text.encode("utf-8")
		data = item.findNext('p').text.encode("utf-8")
		if re.search("Title",header):
			initiative_title = data
			try:
				doc_link = item.findNext('p').a["href"]
			except:
				pass
		elif re.search("Attorney General",header):
			ag = data.split()
			ag_id = ag[0]
			id_note = " ".join(ag[1:])
		elif re.search("Secretary of State",header):
			sos_id = data
		elif re.search("Description",header):
			summary = data
		elif re.search("Proponent",header):
			proponent_block = data
			email_test = re.findall("[a-zA-Z0-9_.]+@\w+\\.\w+",proponent_block)
			if email_test:
				email_adr = email_test[0]
			proponent_str = proponent_block.replace(email_adr,"").strip()
			phone_test = re.findall("\\([0-9]{3}\\)\\s?[0-9]{3}-[0-9]{4}\\s[x][0-9]+|\\([0-9]{3}\\)\\s?[0-9]{3}-[0-9]{4}",proponent_str)
			if phone_test:
				first = True
				for item in phone_test:
					if first:
						first = False
						phone_num = item
					else:
						phone_num = "\n" + item
			proponent = proponent_str.replace(phone_num,"").strip()
		elif re.search("Date",header):
			submit_date = "/".join(data.split("-"))
		elif re.search("Document Type",header):
			doc_type = data
		elif re.search("Qualified",header):
			stat = data
		elif re.search("Citation",header):
			citation = data

	row = [ag_id,id_note,sos_id,initiative_title,summary,doc_link,proponent,email_adr,phone_num,submit_date,doc_type,stat,citation]
	#logging.debug(ag_id)
	return row

def write_data(headers,data):
	ofile = open('scraped/uchastings-initiatives.csv',"wb")
	writer = csv.writer(ofile,delimiter=',',quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow(headers)

	for row in data:
		writer.writerow(row)
	
	ofile.close()
		


if __name__ == '__main__':
	request_url_in('http://repository.uchastings.edu/ca_ballot_inits/')