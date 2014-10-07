#!/usr/bin/python
"""
This script requires a command line argument.
You must tell it what year you want to access on the AG website.
The format looks like this:
scraper-ag-inactive.py -y ####
Ex. 'scraper-ag-inactive.py -y 2013' will fetch inactive initiatives for the year 2013.
"""
import logging
import csv
from optparse import OptionParser
import requests
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup

logging.basicConfig(level=logging.DEBUG)

parser = OptionParser()
parser.add_option("-y", "--year",action="store",type="string",dest="sourceyear",help="choose data year to scrape")
(options,args) = parser.parse_args()

def request_url_in(target_url):
	result = requests.get(target_url)
	content = result.content

	soup = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
	parse_table_from(soup)

def parse_table_from(html):
	data_table = html.find('table')
	data_rows = data_table.findAll('tr')[1:]

	rows = []
	for row in data_rows:
		data_cells = row.findAll('td')
		initiative_details = data_cells[1]
		initiative_title = initiative_details.contents[2].encode("utf-8")
		if data_cells[0].a:
			initiative_id_link = data_cells[0].a["href"]
		else: initiative_id_link = ''
		initiative_id = data_cells[0].text.encode("utf-8")
		
		rows.append([initiative_id,initiative_title.strip(),initiative_id_link])
	headers = ['init_id','title','init_text']	
	write_data(headers,rows)

def write_data(headers,data):
	ofile = open('scraped/ag-inactive-initiatives.csv',"wb")
	writer = csv.writer(ofile,delimiter=',',quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow(headers)

	for row in data:
		writer.writerow(row)
	
	ofile.close()
		


if __name__ == '__main__':
	request_url_in('http://oag.ca.gov/initiatives/inactive-measures?field_initiative_date_value%5Bvalue%5D%5Byear%5D='+options.sourceyear)