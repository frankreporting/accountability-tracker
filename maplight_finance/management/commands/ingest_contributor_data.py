from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from django.core.mail import send_mail, mail_admins, send_mass_mail, EmailMessage
from django.conf import settings
from maplight_finance.models import Initiative, InitiativeContributor
import os
import csv
import logging
import time
import datetime
import urllib2
import requests
import string
from datetime import tzinfo

#logger = logging.getLogger("root")
#logging.basicConfig(
    #format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    #level=logging.DEBUG
#)

logger = logging.getLogger("accountability_tracker")


local_testing_map_light_csvs = [
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-1-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-2-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-45-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-46-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-47-funding_20140924.csv",
    "http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-48-funding_20140924.csv"
]


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
    if map_light_api_request.status_code == 200:
        logger.debug("processing json")
        api_data = map_light_api_request.json()
        api_data = api_data.items()
        list_of_maplight_csvs = []
        for data in api_data:
            data_as_of_date = data[1]["last_funding_update"]
            csv_source = data[1]["funding_csv_file"]
            csv_request = csv_prefix + csv_source
            data_as_of_date = {
                "csv_request": csv_request,
                "data_as_of_date": data_as_of_date
            }
            list_of_maplight_csvs.append(data_as_of_date)
        download_map_light_csv(list_of_maplight_csvs)
    else:
        pass


def download_map_light_csv(list_of_urls):
    """ loop through a list of urls, grab the csv file and write each row to a model """
    for url in list_of_urls:
        response = urllib2.urlopen(url["csv_request"])
        file = csv.reader(response, delimiter=',', quoting=csv.QUOTE_ALL)
        file.next()
        for column in file:
            try:
                transaction = evaluate_transaction_number(column[7], column[0], column[1], column[15], column[11])
                initiative_instance = Initiative.objects.get(initiative_identifier=str(column[0]))
                obj, created = InitiativeContributor.objects.get_or_create(
                    transaction_number = transaction,
                    defaults={
                        "initiative_identifier_id": initiative_instance.id,
                        "stance": str(column[1]),
                        "transaction_name": str(column[2]),
                        "committee_id": str(column[3]),
                        "name": evaluate(str(column[4])),
                        "name_slug": create_name_slug_from(column[4]),
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
                        "transaction_number": transaction,
                        "is_individual": str(column[16]),
                        "donor_type": str(column[17]),
                        "industry": str(column[18]),
                        "data_as_of_date": url["data_as_of_date"]
                    }
                )
                if not created:
                    logger.debug("Record exists")
                else:
                    logger.debug("New record created for %s" % (transaction))
            except Exception, exception:
                logger.error(exception)
                break


def evaluate_transaction_number(city, prop_number, stance, transaction_number, payment_type):
    """ fix if a contribution has no transaction number """
    if prop_number != "":
        slug_prop_number = prop_number.lower().replace(". ", "-")
    else:
        slug_prop_number = "n-a"
    if city != "":
        slug_city = city.lower().replace(" ", "-")
    else:
        slug_city = "n-a"
    if stance != "":
        slug_stance = stance.lower()
    else:
        slug_stance = "n-a"
    if transaction_number != "":
        slug_transaction_number = transaction_number.lower().replace(" ", "")
    else:
        slug_transaction_number = "n-a"
    if payment_type != "":
        slug_payment_type = payment_type.lower().replace(" ", "-")
    else:
        slug_payment_type = "n-a"
    output = "%s-%s-%s-%s-%s" % (slug_prop_number, slug_city, slug_stance, slug_transaction_number, slug_payment_type)
    return output


def evaluate(name):
    """ if name is empty string, give it a name """
    if name == "":
        name = "Unitemized contributions less than 100 dollars"
    else:
        name_list = name.split("(")
        name = name_list[0]
    return name


def create_name_slug_from(name):
    """ strip punctuation and lowercase donor name to create a common format """
    if name == "":
        name = "Unitemized contributions less than 100 dollars"
    output = str(name).replace("&", "and")
    output = output.translate(None, string.punctuation)
    output = output.lower().replace(" ", "-")
    return output


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
        request_map_light_api(settings.MAP_LIGHT_API_KEY)
        #download_map_light_csv(local_testing_map_light_csvs)
        self.stdout.write("\nScraping finished at %s\n" % str(datetime.datetime.now()))