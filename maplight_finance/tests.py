from django.test import TestCase
from django.conf import settings
import datetime
import logging
import csv
import requests
import urllib2

logger = logging.getLogger("accountability_tracker")

# Create your tests here.
class TestCase(TestCase):
    """
    Attempt to test the maplight_finance application
    """

    url = "http://votersedge.org/services_open_api/cvg.contest_v1.json?apikey=938fde1af0f09c4a428e4777d40abc96&contest=M193&date=2014-11-02"

    response = requests.get(url)

    required_keys = [
        "funding_csv_file",
        "last_funding_update",
    ]

    local_testing_map_light_csvs = [
        {'data_as_of_date': u'2014-10-17', 'csv_request': u'http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-48-funding_20141017.csv'},
        {'data_as_of_date': u'2014-10-17', 'csv_request': u'http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-46-funding_20141017.csv'},
        {'data_as_of_date': u'2014-10-17', 'csv_request': u'http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-47-funding_20141017.csv'},
        {'data_as_of_date': u'2014-10-17', 'csv_request': u'http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-2-funding_20141017.csv'},
        {'data_as_of_date': u'2014-10-17', 'csv_request': u'http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-45-funding_20141017.csv'},
        {'data_as_of_date': u'2014-10-17', 'csv_request': u'http://votersedge.org/files/ballot-measures/funding-csv/california-2014-11-prop-1-funding_20141017.csv'}
    ]

    def test_to_get_tests(self):
        """
        This is me learning to test
        """
        a = 2
        b = 2
        self.assertEquals(a, b)

    def test_response_status(self):
        """
        make a request to maplight api
        """
        self.assertEquals(self.response.status_code, 200)

    def test_response_data(self):
        """
        receive JSON data from maplight api
        """
        result = self.response.json()
        self.assertIsNotNone(result)

    def test_data_keys_present(self):
        """
        make sure csv links to initiative contributions are present
        """
        result = self.response.json()
        data = result.items()
        for item in data:
            self.assertIn(self.required_keys[0], item[1])
            self.assertIn(self.required_keys[0], item[1])

    def test_response_csv_file(self):
        """
        make request to csv file
        """
        url = self.local_testing_map_light_csvs[0]
        response = urllib2.urlopen(url["csv_request"])
        self.assertEquals(response.getcode(), 200)

    def test_retrive_csv_file(self):
        """
        test download csv of initiative contributions
        """
        url = self.local_testing_map_light_csvs[0]
        response = urllib2.urlopen(url["csv_request"])
        file = csv.reader(response, delimiter=',', quoting=csv.QUOTE_ALL)
        file.next()
        sample_row = file.next()
        self.assertTrue(sample_row > 0)

    # create a test for the model here...

    def test_convert_date(self):
        """
        test for improper data coming backxxxxxx
        """
        date_string = ""
        self.assertIs(type(date_string), str)

        date_none = None
        self.assertIsNone(date_none)
