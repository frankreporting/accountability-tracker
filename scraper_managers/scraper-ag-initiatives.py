#!/usr/bin/python

import logging
import csv
import requests
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup

logging.basicConfig(level=logging.DEBUG)

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
		anchors = initiative_details.findAll('a')[0:]

		initiative_title = initiative_details.contents[2]
		initiative_id_link = data_cells[0].a["href"]
		initiative_id = data_cells[0].text.encode("utf-8")
		date_link = anchors[0]['href']
		date_block = anchors[0].find('span')['content'].split("-")
		date = date_block[1] + "/" + date_block[2][0:2] + "/" + date_block[0]
		fiscal_impact = anchors[1]['href']
		proponent = initiative_details.contents[9]
		
		rows.append([initiative_id,initiative_title.strip(),initiative_id_link,proponent.strip(),date,date_link,fiscal_impact])
	
	headers = ['init_id','title','init_text','proponent','submit_date','submit_report','fiscal_impact_report']	
	write_data(headers,rows)

def write_data(headers,data):
	ofile = open('scraped/ag-active-initiatives.csv',"wb")
	writer = csv.writer(ofile,delimiter=',',quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow(headers)

	for row in data:
		writer.writerow(row)
	
	ofile.close()
		


if __name__ == '__main__':
	request_url_in('http://oag.ca.gov/initiatives/active-measures')