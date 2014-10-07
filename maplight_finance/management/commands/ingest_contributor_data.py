from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from django.core.mail import send_mail, mail_admins, send_mass_mail, EmailMessage
from django.conf import settings
from maplight_finance.models import InitiativeContributor
import os
import csv
import logging
import time
import datetime
import urllib2
import requests
from datetime import tzinfo

#logger = logging.getLogger("root")
#logging.basicConfig(
    #format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    #level=logging.DEBUG
#)

logger = logging.getLogger("accountability_tracker")


map_light_csvs = [
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-1-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-2-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-45-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-46-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-47-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-48-funding_20140924.csv"
]


def download_map_light_csv(list_of_urls):
    """ loop through a list of urls, grab the csv file and write each row to a model """
    for url in list_of_urls:
        response = urllib2.urlopen(url)
        file = csv.reader(response, delimiter=',', quoting=csv.QUOTE_ALL)
        file.next()
        for column in file:
            try:
                obj, created = InitiativeContributor.objects.get_or_create(
                    transaction_number = str(column[15]),
                    defaults={
                        "initiative_identifier": str(column[0]),
                        "stance": str(column[1]),
                        "transaction_name": str(column[2]),
                        "committee_id": str(column[3]),
                        "name": str(column[4]),
                        "employer": str(column[5]),
                        "occupation": str(column[6]),
                        "city": str(column[7]),
                        "state": str(column[8]),
                        "zip_code": str(column[9]),
                        "id_number": int(column[10]),
                        "payment_type": str(column[11]),
                        "amount": float(column[12]),
                        "transaction_date": convert_date_to_nicey_format(column[13]),
                        "filed_date": convert_date_to_nicey_format(column[14]),
                        "transaction_number": str(column[15]),
                        "is_individual": str(column[16]),
                        "donor_type": str(column[17]),
                        "industry": str(column[18])
                    }
                )
                logger.debug("New record created for %s", (str(column[15])))
            except Exception, exception:
                logger.error(exception)
                break


def request_map_light_api(MAP_LIGHT_API_KEY):
    """ make a request to the Map Light API and return JSON data """
    csv_prefix = "http://votersedge.org/files/ballot-measures/funding-csv/"
    url_prefix = "http://votersedge.org/services_open_api/cvg.contest_v1.json?"
    url_api_key = "apikey=%s" % (MAP_LIGHT_API_KEY)
    url_query = "&contest=M193&date=2014-11-02"
    url_request = "%s%s%s" % (url_prefix, url_api_key, url_query)
    map_light_api_request = requests.get(
        url_request, headers=settings.MAP_LIGHT_API_HEADERS
    )
    api_data = map_light_api_request.json()
    api_data = api_data.items()
    for data in api_data:
        csv_source = data[1]["funding_csv_file"]
        csv_request = csv_prefix + csv_source
        logger.debug(csv_request)


def import_csv_to_model(csv_file):
    """ manager to read a csvfile and write data to model """
    with open(csv_file, 'r', buffering=0) as imported_file:
        file = csv.reader(imported_file, delimiter=',', quoting=csv.QUOTE_ALL)
        file.next()
        for column in file:
            try:
                obj, created = InitiativeContributor.objects.get_or_create(
                    transaction_number = str(column[15]),
                    defaults={
                        "initiative_identifier": str(column[0]),
                        "stance": str(column[1]),
                        "transaction_name": str(column[2]),
                        "committee_id": str(column[3]),
                        "name": str(column[4]),
                        "employer": str(column[5]),
                        "occupation": str(column[6]),
                        "city": str(column[7]),
                        "state": str(column[8]),
                        "zip_code": str(column[9]),
                        "id_number": int(column[10]),
                        "payment_type": str(column[11]),
                        "amount": float(column[12]),
                        "transaction_date": convert_date_to_nicey_format(column[13]),
                        "filed_date": convert_date_to_nicey_format(column[14]),
                        "transaction_number": str(column[15]),
                        "is_individual": str(column[16]),
                        "donor_type": str(column[17]),
                        "industry": str(column[18])
                    }
                )
                logger.debug("New record created for %s", (str(column[15])))
            except Exception, exception:
                logger.error(exception)
    imported_file.close()


def convert_date_to_nicey_format(date):
    """ fix for improper dates coming back """
    if date == "0000-00-00":
        returned_date = "1900-01-01"
    else:
        returned_date = date
    return returned_date


class Command(BaseCommand):
    help = "Imports csv to django model"
    def handle(self, *args, **options):
        #download_map_light_csv(map_light_csvs)
        #request_map_light_api(settings.MAP_LIGHT_API_KEY)
        import_csv_to_model("/Users/KellerUser/Desktop/california-2014-11-prop-45-funding_20140924.csv")
        self.stdout.write("\nScraping finished at %s\n" % str(datetime.datetime.now()))