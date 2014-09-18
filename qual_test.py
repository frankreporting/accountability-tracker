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

# QUALIFIED PROPOSITION SCRAPER TESTS
## Use this to test how the scraper will handle the different ways
##	initiatives and referenda appear on the Sec State's qualified
##	ballot measures page. Initiatives and legislative referrals
##	are formatted differently, for instance, and the information
##	included for each changes over time.
##
## Test cases so far include:
##
##	- InitFirstQualTestCase: initiative first qualifies; has ag_id, sos_id and sig_count_link but no prop number
##	- LegRefFirstQualTestCase: legislative referral first qualifies; has ag_id but no prop_num or sig_count_link
##	- LegRefPropNumAssignedTestCase: legislative referral's prop_num first assigned and still has sos_id
##	- InitPropNumAssignedTestCase: initiative's prop_num first assigned and still has sos_id and ag_id
##	- PropNumOnlyTestCase: after public display, prop_num but ag_id removed
##	- PropNumNoteTestCase: prop_num assigned but with note/asterisk

#Set up test cases here. Use 'checkfields' to show the desired outcomes
TestCases = [
	{'test':'InitPropNumAssignedTestCase',
		'content':'<p id="1541" class="prop-number-ag">Proposition 41 &mdash; 1541. (11-0070)</p>',
		'checkfields':{
			'sos_id':'1541',
			'ag_id':'11-0070',
			'prop_num':'41'}
	},
	{'test':'InitFirstQualTestCase',
		'content':'<p id="1541" class="prop-number-ag">1541. (11-0070) - <a class="prop-link" href="/elections/pend_sig/init-sample-1541-082312.pdf">Final Full Check Update - 08/23/12</a></p><p class="text-strong">Approval of Healthcare Insurance Rate Changes. Initiative Statute.</p><p class="prop-status">Qualified: 08/23/12</p><p>Proponent: Jamie Court</p><p class="prop-text">Requires health insurance rate changes to be approved by Insurance Commissioner before taking effect. Requires sworn statement by health insurer as to accuracy of information submitted to Insurance Commissioner to justify rate changes. Provides for public notice, disclosure and hearing on health insurance rate changes, and subsequent judicial review. Does not apply to employer large group health plans. Prohibits health, auto and homeowners insurers from determining policy eligibility or rates based on lack of prior coverage or credit history. Summary of estimate by Legislative Analyst and Director of Finance of fiscal impact on state and local government: <span class="text-strong">Increased state administrative costs ranging in the low millions to low tens of millions of dollars annually to regulate health insurance rates, funded with revenues collected from filing fees paid by health insurance companies.</span> (11-0070) <a href="http://ag.ca.gov/cms_attachments/initiatives/pdfs/i1013_11-0070_(insurance_affordability).pdf">(Full Text)</a></p>',
		'checkfields':{
			'sos_id':'1541',
			'ag_id':'11-0070',
			'prop_num':'',
			'sig_count_link':'http://www.sos.ca.gov/elections/pend_sig/init-sample-1541-082312.pdf',
			'date_sample_update':'08/23/12',
			'id_note':'Final Full Check Update',
			'initiative_title':'Approval of Healthcare Insurance Rate Changes. Initiative Statute.',
			'date_qualified':'08/23/12',
			'proponent':'Jamie Court',
			'summary':'Requires health insurance rate changes to be approved by Insurance Commissioner before taking effect. Requires sworn statement by health insurer as to accuracy of information submitted to Insurance Commissioner to justify rate changes. Provides for public notice, disclosure and hearing on health insurance rate changes, and subsequent judicial review. Does not apply to employer large group health plans. Prohibits health, auto and homeowners insurers from determining policy eligibility or rates based on lack of prior coverage or credit history. Summary of estimate by Legislative Analyst and Director of Finance of fiscal impact on state and local government:Increased state administrative costs ranging in the low millions to low tens of millions of dollars annually to regulate health insurance rates, funded with revenues collected from filing fees paid by health insurance companies.(11-0070)(Full Text)',
			'full_text_link':'http://ag.ca.gov/cms_attachments/initiatives/pdfs/i1013_11-0070_(insurance_affordability).pdf'}
	},
	{'test':'LegRefFirstQualTestCase',
		'content':'<p id="ab-639" class="prop-number-ag"><a href="/elections/ballot-measures/pdf/sca-17.pdf">SCA 17 (Resolution Chapter 127, Statutes of 2014), Steinberg. Members of the Legislature: suspension.</a></p>',
		'checkfields':{
			'sos_id':'ab-639',
			'ag_id':'',
			'prop_num':'',
			'initiative_title':'SCA 17 (Resolution Chapter 127, Statutes of 2014), Steinberg. Members of the Legislature: suspension.',
			'full_text_link':'http://www.sos.ca.gov/elections/ballot-measures/pdf/sca-17.pdf'}
	},
	{'test':'LegRefPropNumAssignedTestCase',
		'content':'<p id="ab-639" class="prop-number">Proposition 41 &mdash; AB 639. (Chapter 727, 2013), P&eacute;rez.</p><p class="prop-type">Legislative Bond Act</p><p class="prop-title"><a href="/elections/ballot-measures/pdf/ab-639.pdf">Veterans Housing and Homeless Prevention Bond Act of 2014: Veterans Housing and Homeless Prevention Act of 2014</a>.</p>',
		'checkfields':{
			'sos_id':'ab-639',
			'ag_id':'',
			'prop_num':'41',
			'initiative_title':'AB 639. (Chapter 727, 2013), P\xc3\xa9rez. \xe2\x80\x94 Veterans Housing and Homeless Prevention Bond Act of 2014: Veterans Housing and Homeless Prevention Act of 2014.'}
	},
	{'test':'PropNumOnlyTestCase',
		'content':'<p id="prop45" class="prop-number">Proposition 45</p><br /><p class="prop-title"><a href="http://vig.cdn.sos.ca.gov/2014/general/pdf/complete-vig.pdf#page=67">Healthcare Insurance. Rate Changes. Initiative Statute.</a></p>',
		'checkfields':{
			'sos_id':'',
			'ag_id':'',
			'prop_num':'45',
			'full_text_link':'http://vig.cdn.sos.ca.gov/2014/general/pdf/complete-vig.pdf#page=67',
			'initiative_title':'Healthcare Insurance. Rate Changes. Initiative Statute.'}
	},
	{'test':'PropNumNoteTestCase',
		'content':'<p id="prop44" class="prop-number">Proposition 2*</p><br /><p class="prop-title"><a href="http://vig.cdn.sos.ca.gov/2014/general/pdf/complete-vig.pdf#page=64">State Budget. Budget Stabilization Account. Legislative Constitutional Amendment.</a></p><p><span class="text-emphasis">*Senate Bill 867 (Chapter 186, 2014) was signed by the Governor on August 11, 2014; changing the proposition number of this measure from 44 to 2.</span>',
		'checkfields':{
			'sos_id':'',
			'ag_id':'',
			'prop_num':'2',
			'id_note':'*Senate Bill 867 (Chapter 186, 2014) was signed by the Governor on August 11, 2014; changing the proposition number of this measure from 44 to 2.',
			'full_text_link':'http://vig.cdn.sos.ca.gov/2014/general/pdf/complete-vig.pdf#page=64'}
	}
]


def EvaluateTestCase(test_pack):
	test = test_pack["test"]
	content = test_pack["content"]
	checkfields = test_pack["checkfields"]
	data = BeautifulSoup(content, convertEntities=BeautifulSoup.HTML_ENTITIES)
	prop = data.find("p",{"id":True})

	## CODE TO TEST

	#Set defaults
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
	init_status=""
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
	#logging.debug(prop_num + " | " + ag_id + " | " + sos_id)





	## TESTS
	logging.debug("Running tests for " + test + "...")
	logging.debug(prop)
	test_status = 1
	#logging.debug("Locals function returned " + testval + " for date_sum")
	for key, value in checkfields.iteritems():
		if checkfields[key] != locals()[key]:
			logging.debug(key + " should equal " + str(value) + " but instead is " + str(locals()[key]))
			test_status = 0
	if test_status == 1:
		logging.debug("Passed all tests for " + test + ".")
	else:
		logging.debug("One or all of the tests for " + test + " failed.")
	logging.debug("\n\n")

for t in range(len(TestCases)):
	EvaluateTestCase(TestCases[t])