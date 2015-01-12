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
from dateutil import parser

logger = logging.getLogger("accountability_tracker")

class MapLightApiRequest(object):
    """
    scaffolding to make an api request to MapLight and return ballot initiative contributions
    """
    csv_prefix = "http://votersedge.org/files/ballot-measures/funding-csv/"
    url_prefix = "http://votersedge.org/services_open_api/cvg.contest_v1.json?"
    url_api_key = "apikey=%s" % (settings.MAP_LIGHT_API_KEY)
    url_query = "&contest=M193&date=2014-11-02"
    url_request = "%s%s%s" % (url_prefix, url_api_key, url_query)

    def _init(self, *args, **kwargs):
        """
        run the functions needed to get contributors
        """
        api_data = self.request_data_and_return(self.url_request)
        list_of_maplight_csvs = self.get_csv_links_from(api_data)
        for csv_url in list_of_maplight_csvs:
            self.download_map_light_csv(csv_url)

    def request_data_and_return(self, url):
        """
        make a request to the Map Light API and receive JSON data
        """
        response = requests.get(url, headers=settings.MAP_LIGHT_API_HEADERS)
        if response.status_code == 200:
            result = response.json()
            api_data = result.items()
            return api_data
        else:
            return False

    def get_csv_links_from(self, list):
        """
        isolate csv links to initiative contributions
        """
        container = []
        for item in list:
            data_as_of_date = item[1]["last_funding_update"]
            csv_source = item[1]["funding_csv_file"]
            csv_request = "%s%s" % (self.csv_prefix, csv_source)
            initiative_instance = {
                "csv_request": csv_request,
                "data_as_of_date": data_as_of_date
            }
            container.append(initiative_instance)
        return container

    def download_map_light_csv(self, url):
        """
        download csv of initiative contributions
        """
        response = urllib2.urlopen(url["csv_request"])
        file = csv.reader(response, delimiter=',', quoting=csv.QUOTE_ALL)
        file.next()
        for record in file:
            self.write_data_to_model(record, url["data_as_of_date"])

    def open_map_light_csv(self, file_path):
        """
        manager to read a csvfile in order to write the data to a model
        """
        with open(file_path, 'r', buffering=0) as response:
            file = csv.reader(response, delimiter=',', quoting=csv.QUOTE_ALL)
            file.next()
            for record in file:
                self.write_data_to_model(record, parser.parse("11/01/2014"))

    def write_data_to_model(self, record, data_as_of_date):
        """
        take a row of data from a csv and create a model instance in the db
        """
        format = FormatUtilities()
        try:
            transaction = format.evaluate_transaction_number(record[7], record[0], record[1], record[15], record[11])
            initiative_instance = Initiative.objects.get(initiative_identifier=str(record[0]))
            obj, created = InitiativeContributor.objects.get_or_create(
                transaction_number = transaction,
                defaults={
                    "initiative_identifier_id": initiative_instance.id,
                    "stance": str(record[1]),
                    "transaction_name": str(record[2]),
                    "committee_id": str(record[3]),
                    "name": format.evaluate(str(record[4])),
                    "name_slug": format.create_name_slug_from(record[4]),
                    "employer": str(record[5]),
                    "occupation": str(record[6]),
                    "city": str(record[7]),
                    "state": str(record[8]),
                    "zip_code": str(record[9]),
                    "id_number": int(record[10]),
                    "payment_type": str(record[11]),
                    "amount": float(record[12]),
                    "transaction_date": format.convert_date_to_nicey_format(record[13]),
                    "filed_date": format.convert_date_to_nicey_format(record[14]),
                    "transaction_number": transaction,
                    "is_individual": str(record[16]),
                    "donor_type": str(record[17]),
                    "industry": str(record[18]),
                    "data_as_of_date": data_as_of_date
                }
            )
            if not created:
                logger.debug("Record exists")
            else:
                logger.debug("New record created for %s" % (transaction))
        except Exception, exception:
            logger.error(exception)
            raise


class FormatUtilities(object):
    def evaluate_transaction_number(self, city, prop_number, stance, transaction_number, payment_type):
        """
        fix if a contribution has no transaction number
        """
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

    def evaluate(self, name):
        """
        if name is empty string, give it a name
        """
        if name == "":
            output = "Unitemized contributions less than 100 dollars"
        else:
            name_list = name.split("(")
            output = name_list[0]
        return output

    def create_name_slug_from(self, name):
        """
        strip punctuation and lowercase donor name to create a common format
        """
        if name == "":
            name = "Unitemized contributions less than 100 dollars"
        output = str(name).replace("&", "and")
        output = output.translate(None, string.punctuation)
        output = output.lower().replace(" ", "-")
        return output

    def convert_date_to_nicey_format(self, date):
        """
        fix for improper dates coming back
        """
        if date is None or date is "":
            output = "1900-01-01"
        elif date == "0000-00-00":
            output = "1900-01-01"
        else:
            output = parser.parse(date)
        return output


class Command(BaseCommand):
    help = "Begin a request to the MapLight API"
    def handle(self, *args, **options):
        task_run = MapLightApiRequest()

        # run the main functions
        task_run._init()

        # create model instances from local csv file
        #task_run.open_map_light_csv("/Users/ckeller/Desktop/california-2014-11-prop-1-funding_20140924.csv")
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
