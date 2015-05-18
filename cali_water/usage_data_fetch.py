from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from cali_water.models import WaterSupplier, WaterSupplierMonthlyReport
import csv
from csvkit.utilities.in2csv import In2CSV
import re
import logging
import time
import datetime
import requests
from dateutil import parser
from collections import OrderedDict
import sys
import os.path

logger = logging.getLogger("accountability_tracker")

class BuildMonthlyWaterUseReport(object):
    """
    scaffolding to ...
    """
    # needs a test
    list_of_files = [
        "http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/0505015uw_supplier_data.xlsx",
        #"http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data040715.xlsx",
        #"http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data030315.xlsx",
        #"http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data020315.xlsx",
        #"http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data010215.xlsx",
        #"http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data120214.xlsx",
        #"http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/emergency_regulations/uw_supplier_data110414.xlsx",
        #"http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/uw_supplier_data100714.xlsx",
        #"http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/workshops/urban_water_conservation_mandatory_results091114.xlsx",
    ]

    download_path = "/Volumes/one_tb_hd/_programming/2kpcc/django-projects/accountability_tracker/cali_water"

    list_latest_keys = [
        "Supplier Name",
        "Stage Invoked",
        "Mandatory Restrictions",
        "Reporting Month",
        "Total Monthly Potable Water Production 2014/2015",
        "Total Monthly Potable Water Production 2013",
        "Units",
        "Qualification",
        "Total Population Served",
        "REPORTED Residential Gallons-per-Capita-Day (R-GPCD) (starting in September 2014)",
        "Optional - Enforcement Actions",
        "Optional - Implementation",
        "Optional - Recycled Water",
        "Recycled Water Units",
        "CALCULATED Production Monthly Gallons Month 2014/2015",
        "CALCULATED Production Monthly Gallons Month 2013",
        "CALCULATED R-GPCD 2014/2015 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)",
        "CALCULATED R-GPCD 2013 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)",
        "% Residential Use",
        "Comments/Corrections",
        "Hydrologic Region",
    ]

    list_20_keys = [
        "Supplier Name",
        "Stage Invoked",
        "Mandatory Restrictions",
        "Reporting Month",
        "Total Monthly Potable Water Production 2014",
        "Total Monthly Potable Water Production 2013",
        "Units",
        "Qualification",
        "Total Population Served",
        "REPORTED Residential Gallons-per-Capita-Day (R-GPCD) (starting in September 2014)",
        "Optional - Enforcement Actions",
        "Optional - Implementation",
        "Optional - Recycled Water",
        "Recycled Water Units",
        "CALCULATED Monthly Gallons Month 2014",
        "CALCULATED Monthly Gallons Month 2013",
        "CALCULATED R-GPCD 2014 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)",
        "CALCULATED R-GPCD 2013 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)",
        "% Residential Use",
        "Comments/Corrections",
    ]

    list_older_keys = [
        "Supplier Name",
        "Stage Invoked",
        "Mandatory Restrictions",
        "Reporting Month",
        "Total Monthly Potable Water Production 2014",
        "Total Monthly Potable Water Production 2013",
        "Units",
        "Qualification",
        "Total Population Served",
        "Optional - Enforcement Actions",
        "Optional - Implementation",
        "Optional - Recycled Water",
        "Recycled Water Units",
        "CALCULATED Monthly Gallons Month 2014",
        "CALCULATED Monthly Gallons Month 2013",
        "% Residential Use",
        "Comments/Corrections",
    ]

    def _init(self, *args, **kwargs):
        """
        begin the process of downloading the latest state water control board usage report
        """
        for file_url in self.list_of_files:
            if file_url == "http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/emergency_regulations/uw_supplier_data110414.xlsx":
                report_date = file_url.split("http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/emergency_regulations/")[1]
            elif file_url == "http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/workshops/urban_water_conservation_mandatory_results091114.xlsx":
                report_date = file_url.split("http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/workshops/urban_water_conservation_mandatory_results")[1]
                report_date = "uw_supplier_data%s" % (report_date)
            elif file_url == "http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/0505015uw_supplier_data.xlsx":
                report_date = file_url.split("http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/")[1]
            else:
                report_date = file_url.split("http://www.swrcb.ca.gov/waterrights/water_issues/programs/drought/docs/")[1]
            file_name = "%s/%s" % (self.download_path, report_date)

            created_csv_file = "%s/%s" % (self.download_path, report_date.replace("xlsx", "csv"))

            #self._download_water_use_data(file_url, file_name, created_csv_file)

            comparison_check = self._check_column_headers_against(created_csv_file)

            if comparison_check["status"] == True:
                self._build_model_from(comparison_check, report_date, created_csv_file)
            else:
                print "ISSUE WITH COLUMN HEADERS: I can not process %s" % (created_csv_file)

    def _download_water_use_data(self, file_url, file_name, created_csv_file):
        """
        downloads the excel report and converts the file to csv
        """
        print "Downloading %s" % (file_name)
        try:
            print "Requesting state water usage report"
            response = requests.get(file_url, headers=settings.REQUEST_HEADERS)
            if response.status_code == 200:
                if response.content != None:
                    print "Received state water usage data"
                    with open(file_name, "w+", buffering=-1) as output_file:
                        print "Writing the excel file"
                        output_file.write(response.content)
                    excel_file_written = os.path.isfile(file_name)
                    excel_file_size = os.path.getsize(file_name)
                    args = ["-f", "xlsx", file_name]
                    with open(created_csv_file, "w+", buffering=-1) as output_file:
                        utility = In2CSV(args, output_file).main()
                    csv_file_written = os.path.isfile(created_csv_file)
                    print "Writing %s" % (created_csv_file)
                    csv_file_size = os.path.getsize(file_name)
                else:
                    return False
            else:
                return False
        except Exception, exception:
            logger.error(exception)
            raise

    def _check_column_headers_against(self, created_csv_file):
        """
        builds data for database from csv file
        """
        with open(created_csv_file, "rb") as csvfile:
            csv_data = csv.reader(csvfile, delimiter=',')
            list_downloaded_headers = csv_data.next()
            num_downloaded_keys = len(list_downloaded_headers)
            num_latest_keys = len(self.list_latest_keys)
            num_20_keys = len(self.list_20_keys)
            num_older_keys = len(self.list_older_keys)
            status = {}
            if num_downloaded_keys == num_latest_keys:
                status["status"] = self._compare_lists(list_downloaded_headers, self.list_latest_keys)
                status["column_structure"] = self.list_latest_keys
            elif num_downloaded_keys == num_20_keys:
                status["status"] = self._compare_lists(list_downloaded_headers, self.list_20_keys)
                status["column_structure"] = self.list_20_keys
            elif num_downloaded_keys == num_older_keys:
                status["status"] = self._compare_lists(list_downloaded_headers, self.list_older_keys)
                status["column_structure"] = self.list_older_keys
            else:
                status["status"] = False
                status["column_structure"] = None
            return status

    def _build_model_from(self, comparison_check, report_date, created_csv_file):
        """
        builds data for database from csv file
        """

        column_structure = comparison_check["column_structure"]

        with open(created_csv_file, "rb") as csvfile:

            csv_data = csv.DictReader(csvfile, delimiter=',')

            for row in csv_data:

                clean_row = {k.strip(): v.strip() for k, v in row.iteritems()}

                supplier_formatted = self._prettify_and_slugify(clean_row["Supplier Name"])

                data_to_process = {}

                data_to_process["supplier_name"] = supplier_formatted[1]

                data_to_process["supplier_slug"] = supplier_formatted[0]

                data_to_process["supplier_url"] = None

                data_to_process["supplier_mwd_member"] = False

                try:
                    data_to_process["hydrologic_region"] = clean_row["Hydrologic Region"]
                except Exception, exception:
                    data_to_process["hydrologic_region"] = None
                    #print "%s %s %s" % (created_csv_file, exception, clean_row)
                    #raise

                if data_to_process["hydrologic_region"] != None:
                    data_to_process["hydrologic_region_slug"] = self._create_hydrologic_region_slug(data_to_process["hydrologic_region"])
                else:
                    data_to_process["hydrologic_region_slug"] = None

                data_to_process["created_date"] = datetime.datetime.now()

                data_to_process["supplier_notes"] = None

                data_to_process["stage_invoked"] = clean_row["Stage Invoked"]

                if clean_row["Mandatory Restrictions"] == "Yes":
                    data_to_process["mandatory_restrictions"] = True
                else:
                    data_to_process["mandatory_restrictions"] = False

                try:
                    year = clean_row["Reporting Month"][-2:]
                    month = clean_row["Reporting Month"][:-2]
                    if len(month) == 2:
                        this_month = month
                    else:
                        this_month = "0%s" % (month)
                    day = 1
                    my_reporting_month = "20%s-%s-0%s" % (year, this_month, day)
                    #my_reporting_month = clean_row["Reporting Month"].replace("-", " 20")
                    data_to_process["reporting_month"] = parser.parse(my_reporting_month)
                except:
                    try:
                        year = clean_row["Reporting Month"][-2:]
                        month = clean_row["Reporting Month"][:-2]
                        if len(month) == 2:
                            this_month = month
                        else:
                            this_month = "0%s" % (month)
                        day = 1
                        my_reporting_month = "20%s-%s-0%s" % (year, this_month, day)
                        logger.debug(my_reporting_month)

                        #my_reporting_month = clean_row["Reporting Month"]
                        data_to_process["reporting_month"] = parser.parse(my_reporting_month)
                    except Exception, exception:
                        data_to_process["total_monthly_potable_water_production_2014"] = None
                        print "%s %s %s" % (created_csv_file, exception, clean_row)
                        #raise

                try:
                    data_to_process["total_monthly_potable_water_production_2014"] = float(clean_row["Total Monthly Potable Water Production 2014/2015"].replace(",", ""))
                except:
                    try:
                        data_to_process["total_monthly_potable_water_production_2014"] = float(clean_row["Total Monthly Potable Water Production 2014/2015"].replace(",", ""))
                    except Exception, exception:
                        #data_to_process["total_monthly_potable_water_production_2014"] = None
                        print "%s %s %s" % (created_csv_file, exception, clean_row)
                        raise

                try:
                    data_to_process["total_monthly_potable_water_production_2013"] = float(clean_row["Total Monthly Potable Water Production 2013"].replace(",", ""))
                except Exception, exception:
                    #data_to_process["total_monthly_potable_water_production_2013"] = None
                    print "%s %s %s" % (created_csv_file, exception, clean_row)
                    raise

                data_to_process["units"] = clean_row["Units"].upper()

                data_to_process["qualification"] = clean_row["Qualification"]

                try:
                    clean_row["Total Population Served"] = clean_row["Total Population Served"].replace(",", "")
                    population_as_float = float(clean_row["Total Population Served"])
                    data_to_process["total_population_served"] = int(population_as_float)
                except Exception, exception:
                    clean_row["Total Population Served"] = clean_row["Total Population Served"].replace(",", "")
                    population_as_float = float(clean_row["Total Population Served"])
                    data_to_process["total_population_served"] = int(population_as_float)
                    print "%s %s %s" % (created_csv_file, exception, clean_row)
                    #raise

                try:
                    data_to_process["reported_rgpcd"] = float(clean_row["REPORTED Residential Gallons-per-Capita-Day (R-GPCD) (starting in September 2014)"])
                except Exception, exception:
                    data_to_process["reported_rgpcd"] = None
                    print "%s %s %s" % (created_csv_file, exception, clean_row)
                    #raise

                data_to_process["enforcement_actions"] = clean_row["Optional - Enforcement Actions"]

                data_to_process["implementation"] = clean_row["Optional - Implementation"]

                data_to_process["recycled_water"] = clean_row["Optional - Recycled Water"]

                data_to_process["recycled_water_units"] = clean_row["Recycled Water Units"]

                try:
                    clean_data = clean_row["CALCULATED Production Monthly Gallons Month 2014/2015"].replace(",", "")
                    data_to_process["calculated_production_monthly_gallons_month_2014"] = float(clean_data)
                except:
                    try:
                        clean_data = clean_row["CALCULATED Production Monthly Gallons Month 2014"].replace(",", "")
                        data_to_process["calculated_production_monthly_gallons_month_2014"] = float(clean_data)
                    except:
                        try:
                            clean_data = clean_row["CALCULATED Monthly Gallons Month 2014"].replace(",", "")
                            data_to_process["calculated_production_monthly_gallons_month_2014"] = float(clean_data)
                        except Exception, exception:
                            data_to_process["calculated_production_monthly_gallons_month_2014"] = None
                            print "%s %s %s" % (created_csv_file, exception, clean_row)
                            #raise

                try:
                    clean_data = clean_row["CALCULATED Production Monthly Gallons Month 2013"].replace(",", "")
                    data_to_process["calculated_production_monthly_gallons_month_2013"] = float(clean_data)
                except:
                    try:
                        clean_data = clean_row["CALCULATED Monthly Gallons Month 2013"].replace(",", "")
                        data_to_process["calculated_production_monthly_gallons_month_2013"] = float(clean_data)
                    except Exception, exception:
                        data_to_process["calculated_production_monthly_gallons_month_2013"] = None
                        print "%s %s %s" % (created_csv_file, exception, clean_row)
                        #raise

                try:
                    data_to_process["calculated_rgpcd_2014"] = float(clean_row["CALCULATED R-GPCD 2014/2015 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)"])
                except:
                    try:
                        data_to_process["calculated_rgpcd_2014"] = float(clean_row["CALCULATED R-GPCD 2014 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)"])
                    except Exception, exception:
                        data_to_process["calculated_rgpcd_2014"] = None
                        print "%s %s %s" % (created_csv_file, exception, clean_row)
                        #raise

                try:
                    data_to_process["calculated_rgpcd_2013"] = float(clean_row["CALCULATED R-GPCD 2013 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)"])
                except Exception, exception:
                    data_to_process["calculated_rgpcd_2013"] = None
                    print "%s %s %s" % (created_csv_file, exception, clean_row)
                    #raise

                try:
                    data_to_process["percent_residential_use"] = float(int(clean_row["% Residential Use"]) / 100)
                except:
                    try:
                        clean_data = clean_row["% Residential Use"].replace("%", "")
                        data_to_process["percent_residential_use"] = float(clean_data)
                    except Exception, exception:
                        #data_to_process["percent_residential_use"] = None
                        print "%s %s %s" % (created_csv_file, exception, clean_row)
                        raise

                data_to_process["comments_or_corrections"] = clean_row["Comments/Corrections"]

                try:
                    #data_to_process["report_date"] = self._extract_date_of_report(report_date)
                    data_to_process["report_date"] = self._extract_date_of_report(report_date)
                except Exception, exception:
                    #data_to_process["report_date"] = self._extract_date_of_report(report_date)
                    print "%s %s %s" % (created_csv_file, exception, clean_row)
                    #raise

                logger.debug(data_to_process)

                self._save_supplier_instance_from(data_to_process)
                self._save_supplier_report_instance_from(data_to_process)

    def _save_supplier_instance_from(self, data):
        """
        save water supplier model instance from dictionary
        """
        try:
            obj, created = WaterSupplier.objects.get_or_create(
                supplier_slug = data["supplier_slug"],
                defaults = {
                    "supplier_name": data["supplier_name"],
                    "supplier_url": data["supplier_url"],
                    "supplier_mwd_member": data["supplier_mwd_member"],
                    "hydrologic_region": data["hydrologic_region"],
                    "created_date": data["created_date"],
                    "supplier_notes": data["supplier_notes"],
                }
            )
            if not created:
                logger.debug("%s exists" % (data["supplier_name"]))
            elif created:
                logger.debug("%s created: %s - %s" % (data["supplier_name"], data["supplier_slug"], data["hydrologic_region"]))
        except ValueError, exception:
            traceback.print_exc(file=sys.stdout)
            logger.debug("%s-%s" % (exception, data["supplier_name"]))

    def _save_supplier_report_instance_from(self, data):
        """
        * save monthly water supplier model instance from dictionary
        * spreadsheet has 2,419 rows
        * the following have duplicates for june and jul
            * city of gilroy - 2014-06-01 00:00:00 exists
            * city of gilroy - 2014-06-01 00:00:00 exists
            * city of indio - 2014-06-01 00:00:00 exists
            * olivehurst public utility district - 2014-07-01 00:00:00 exists
            * placer county water agency - 2014-07-01 00:00:00 exists
            * california water service company mid peninsula - 2014-09-01 00:00:00 exists
            * city of palo alto - 2014-08-01 00:00:00 exists
            * city of palo alto - 2014-07-01 00:00:00 exists
            * city of modesto - 2014-08-01 00:00:00 exists
            * city of modesto - 2014-08-01 00:00:00 exists
            * city of beverly hills - 2014-06-01 00:00:00 exists
            * city of perris - 2014-07-01 00:00:00 exists
            * city of perris - 2014-06-01 00:00:00 exists
            * city of pomona - 2014-08-01 00:00:00 exists
            * city of pomona - 2014-07-01 00:00:00 exists
            * city of pomona - 2014-06-01 00:00:00 exists
        """
        try:
            supplier = WaterSupplier.objects.get(supplier_slug = data["supplier_slug"])
            report, created = supplier.watersuppliermonthlyreport_set.get_or_create(
                report_date = data["report_date"],
                supplier_name = data["supplier_name"],
                reporting_month = data["reporting_month"],
                defaults = {
                    "supplier_slug": data["supplier_slug"],
                    "stage_invoked": data["stage_invoked"],
                    "mandatory_restrictions": data["mandatory_restrictions"],
                    "reporting_month": data["reporting_month"],
                    "total_monthly_potable_water_production_2014": data["total_monthly_potable_water_production_2014"],
                    "total_monthly_potable_water_production_2013": data["total_monthly_potable_water_production_2013"],
                    "units": data["units"].upper(),
                    "qualification": data["qualification"],
                    "total_population_served": data["total_population_served"],
                    "reported_rgpcd": data["reported_rgpcd"],
                    "enforcement_actions": data["enforcement_actions"],
                    "implementation": data["implementation"],
                    "recycled_water": data["recycled_water"],
                    "recycled_water_units": data["recycled_water_units"],
                    "calculated_production_monthly_gallons_month_2014": data["calculated_production_monthly_gallons_month_2014"],
                    "calculated_production_monthly_gallons_month_2013": data["calculated_production_monthly_gallons_month_2013"],
                    "calculated_rgpcd_2014": data["calculated_rgpcd_2014"],
                    "calculated_rgpcd_2013": data["calculated_rgpcd_2013"],
                    "percent_residential_use": data["percent_residential_use"],
                    "comments_or_corrections": data["comments_or_corrections"],
                    "hydrologic_region": data["hydrologic_region"],
                    "hydrologic_region_slug": data["hydrologic_region_slug"],
                }
            )
            if not created:
                logger.debug("%s - %s exists" % (data["supplier_name"], data["reporting_month"]))
            elif created:
                logger.debug("%s - %s created" % (data["supplier_name"], data["reporting_month"]))
        except ObjectDoesNotExist, exception:
            logger.error("%s %s" % (exception, data["supplier_slug"]))

    def _prettify_and_slugify(self, string):
        """
        convert a water supplier name to a slug
        """
        # get regex to find "City of"
        more_than_one_space = re.compile("\s+")

        string = string.lower()
        value = re.sub("[^0-9a-zA-Z\s-]+", " ", string)

        city_in = "city" in value
        town_in = "town" in value

        if city_in == True:
            start_city_check = re.compile("^city of")
            end_city_check = re.compile("city of")
            city_match = re.search(start_city_check, value)
            try:
                if city_match:
                    pretty_name = value
                else:
                    end_city_match = re.search(end_city_check, value)
                    if end_city_match:
                        value = value.split("city of")
                        pretty_name = "city of %s" % (value[0].strip())
                    else:
                        pretty_name = value
            except Exception, exception:
                logger.error(exception)
                raise
        elif town_in == True:
            start_town_check = re.compile("^town of")
            end_town_check = re.compile("town of")
            town_match = re.search(start_town_check, value)
            try:
                if town_match:
                    pretty_name = value
                else:
                    end_town_match = re.search(end_town_check, value)
                    if end_town_match:
                        value = value.split("town of")
                        pretty_name = "town of %s" % (value[0].strip())
                    else:
                        pretty_name = value
            except Exception, exception:
                logger.error(exception)
                raise
        else:
            pretty_name = value

        # remove extra spaces
        pretty_name = " ".join(pretty_name.split())

        # format to use as slug
        slug = pretty_name.encode("ascii", "ignore").lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
        slug = re.sub(r"[-]+", "-", slug)
        output = [slug, pretty_name]
        return  output

    def _create_hydrologic_region_slug(self, item):
        value = item.encode("ascii", "ignore").lower().strip().replace(" ", "-")
        value = re.sub(r"[^\w-]", "", value)
        return value

    def _extract_date_of_report(self, report_date):
        """
        extract the date a report is released based on file name
        """
        #split_data = report_date.split(".")
        #target_date = split_data[0][-6:]
        #month = int(target_date[:2])
        #day = int(target_date[2:4])
        #year = 2000 + int(target_date[4:6])
        #output = datetime.date(year, month, day)
        output = datetime.date(2015, 5, 5)
        return output

    def _compare_lists(self, list1, list2):
        for i in range(len(list1)):
            if list1[i] == list2[i]:
                continue
            else:
                break
        return True

if __name__ == '__main__':
    task_run = BuildWaterUseReport()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
