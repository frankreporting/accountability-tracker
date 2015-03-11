from django.test import TestCase
from django.conf import settings
from cali_water.fetch_usage_data import BuildMonthlyWaterUseReport
import csv
from csvkit.utilities.in2csv import In2CSV
import re
import logging
import time
import datetime
import requests
import os.path

logger = logging.getLogger("accountability_tracker")

# Create your tests here.
class TestCase(TestCase):
    """
    Attempt to test the cali_water application
    """

    def setUp(self):
        run = BuildMonthlyWaterUseReport()

        self.list_of_files = run.list_of_files
        self.download_url = run.download_url

        self.file_name = "%s/_test_%s" % (run.download_path, run.report_date)
        self.created_csv_file = "%s/_test_%s" % (run.download_path, run.report_date.replace("xlsx", "csv"))

        #does_excel_file_exist = os.path.isfile(self.file_name)
        #if does_excel_file_exist == True:
            #os.remove(self.file_name)

        #does_csv_file_exist = os.path.isfile(self.created_csv_file)
        #if does_csv_file_exist == True:
            #os.remove(self.created_csv_file)


    def _NOT_test_download_water_use_data(self):
        """
        test to download excel report and convert file to csv
        """
        try:
            print "Requesting state water usage report"
            response = requests.get(self.download_url, headers=settings.REQUEST_HEADERS)
            if response.status_code == 200:
                if response.content != None:
                    print "Received state water usage data"
                    with open(self.file_name, "w+", buffering=-1) as output_file:
                        print "Writing the excel file"
                        output_file.write(response.content)
                    excel_file_written = os.path.isfile(self.file_name)
                    excel_file_size = os.path.getsize(self.file_name)
                    args = ["-f", "xlsx", self.file_name]
                    with open(self.created_csv_file, "w+", buffering=-1) as output_file:
                        utility = In2CSV(args, output_file).main()
                    csv_file_written = os.path.isfile(self.created_csv_file)
                    csv_file_size = os.path.getsize(self.file_name)
                else:
                    return False
            else:
                return False
        except Exception, exception:
            logger.error(exception)
            raise

        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(response.content)
        self.assertTrue(excel_file_written)
        self.assertTrue(excel_file_size > 0)
        self.assertTrue(csv_file_written)
        self.assertTrue(csv_file_size > 0)

    def test_build_model_from(self):
        """
        builds data for database from csv file
        """
        with open(self.created_csv_file, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                self.assertTrue(row.has_key("Supplier Name"))
                self.assertTrue(row.has_key("Stage Invoked"))
                self.assertTrue(row.has_key("Mandatory Restrictions"))
                self.assertTrue(row.has_key("Reporting Month"))
                self.assertTrue(row.has_key("Total Monthly Potable Water Production 2014"))
                self.assertTrue(row.has_key("Total Monthly Potable Water Production 2013"))
                self.assertTrue(row.has_key("Units"))
                self.assertTrue(row.has_key("Qualification"))
                self.assertTrue(row.has_key("Total Population Served"))
                self.assertTrue(row.has_key("REPORTED Residential Gallons-per-Capita-Day (R-GPCD) (starting in September 2014)"))
                self.assertTrue(row.has_key("Optional - Enforcement Actions,Optional - Implementation"))
                self.assertTrue(row.has_key("Optional - Recycled Water"))
                self.assertTrue(row.has_key("Recycled Water Units"))
                self.assertTrue(row.has_key("CALCULATED Production Monthly Gallons Month 2014"))
                self.assertTrue(row.has_key("CALCULATED Production Monthly Gallons Month 2013"))
                self.assertTrue(row.has_key("CALCULATED R-GPCD 2014 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)"))
                self.assertTrue(row.has_key("CALCULATED R-GPCD 2013 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)"))
                self.assertTrue(row.has_key("% Residential Use"))
                self.assertTrue(row.has_key("Comments/Corrections"))
                self.assertTrue(row.has_key("Hydrologic Region"))




                #data_to_process["stage_invoked"] = row["Stage Invoked"]
                #if row["Mandatory Restrictions"] == "Yes":
                    #data_to_process["mandatory_restrictions"] = True
                #else:
                    #data_to_process["mandatory_restrictions"] = False
                #data_to_process["reporting_month"] = parser.parse(row["Reporting Month"])
                #try:
                    #data_to_process["total_monthly_potable_water_production_2014"] = float(row["Total Monthly Potable Water Production 2014"])
                #except:
                    #data_to_process["total_monthly_potable_water_production_2014"] = None
                #try:
                    #data_to_process["total_monthly_potable_water_production_2013"] = float(row["Total Monthly Potable Water Production 2013"])
                #except:
                    #data_to_process["total_monthly_potable_water_production_2013"] = None
                #data_to_process["units"] = row["Units"]
                #data_to_process["qualification"] = row["Qualification"]
                #data_to_process["total_population_served"] = int(row["Total Population Served"])
                #try:
                    #data_to_process["reported_rgpcd"] = float(row["REPORTED Residential Gallons-per-Capita-Day (R-GPCD) (starting in September 2014)"])
                #except:
                    #data_to_process["reported_rgpcd"] = None
                #data_to_process["enforcement_actions"] = row["Optional - Enforcement Actions"]
                #data_to_process["implementation"] = row["Optional - Implementation"]
                #data_to_process["recycled_water"] = row["Optional - Recycled Water"]
                #data_to_process["recycled_water_units"] = row["Recycled Water Units"]
                #try:
                    #data_to_process["calculated_production_monthly_gallons_month_2014"] = float(row["CALCULATED Production Monthly Gallons Month 2014"])
                #except:
                    #data_to_process["calculated_production_monthly_gallons_month_2014"] = None
                #try:
                    #data_to_process["calculated_production_monthly_gallons_month_2013"] = float(row["CALCULATED Production Monthly Gallons Month 2013"])
                #except:
                    #data_to_process["calculated_production_monthly_gallons_month_2013"] = None
                #try:
                    #data_to_process["calculated_rgpcd_2014"] = float(row["CALCULATED R-GPCD 2014 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)"])
                #except:
                    #data_to_process["calculated_rgpcd_2014"] = None
                #try:
                    #data_to_process["calculated_rgpcd_2013"] = float(row["CALCULATED R-GPCD 2013 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)"])
                #except:
                    #data_to_process["calculated_rgpcd_2013"] = None
                #data_to_process["percent_residential_use"] = float(row["% Residential Use"])
                #data_to_process["comments_or_corrections"] = row["Comments/Corrections"]
                #data_to_process["report_date"] = self.report_date
