#!/usr/bin/python

import logging
import csv
import re
from optparse import OptionParser

logging.basicConfig(level=logging.DEBUG)

parser = OptionParser()
parser.add_option("-f", "--file",action="store",type="string",dest="filename",help="choose '-f' or '--file' and name of file")
(options,args) = parser.parse_args()


def read_data(csvFile):
	rows = []
	with open(csvFile, 'rU') as f:
		reader = csv.reader(f,dialect='excel',quotechar='"',quoting=csv.QUOTE_ALL)
		for row in reader:
			rows.append(row)
	f.close()
	
	headers = rows[0]
	for i in range(len(headers)):
		att = str(headers[i])
		att = "".join(att.split()).strip()
		headers[i] = att

	data_len = len(headers)
	contacts = []
	iterrows = iter(rows)
	next(iterrows)
	for row in iterrows:
		contact = {}
		for y in range(data_len):
			contact[headers[y]] = row[y]
		contacts.append(contact)
	
	"""
	for num in range(10):
		logging.debug(contacts[num]['LastName'])
	"""
	return contacts
		


if __name__ == '__main__':
	read_data(options.filename)