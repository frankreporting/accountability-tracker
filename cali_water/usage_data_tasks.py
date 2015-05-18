from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Avg, Max, Min, Sum, Count
from cali_water.models import WaterSupplier, WaterSupplierMonthlyReport, WaterEnforcementMonthlyReport
from cali_water.views import QueryUtilities
from cali_water.usage_data_fetch import BuildMonthlyWaterUseReport
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

class TasksForMonthlyWaterUseReport(object):

    def _init(self, *args, **kwargs):
        """
        begin the process of downloading the latest state water control board usage report
        """
        #logger.debug("Choose a function to run")
        #self.add_hydrologic_region_to_watersuppliermonthlyreport()
        #self.add_hydrologic_region_slug_to_watersuppliermonthlyreport()
        #self.add_supplier_slug_to_watersuppliermonthlyreport
        #self.fix_dates_on_reports()
        #self.model_first_and_second_reduction_proposals()
        #self.model_third_reduction_proposals("/Users/ckeller/Desktop/third_proposal_5-4-15.csv")
        #self.model_monthly_enforcement_stats("/Users/ckeller/Desktop/050515enforcement_statistics.csv")

    def add_hydrologic_region_to_watersuppliermonthlyreport(self):
        queryset = WaterSupplierMonthlyReport.objects.all()
        for item in queryset:
            if item.hydrologic_region == None:
                parent_obj = WaterSupplier.objects.get(supplier_name = item.supplier_name_id)
                item.hydrologic_region = parent_obj.hydrologic_region
                logger.debug(item.hydrologic_region)
                item.save()
            else:
                logger.debug("Everything's cool!")

    def add_hydrologic_region_slug_to_watersuppliermonthlyreport(self):
        queryset = WaterSupplierMonthlyReport.objects.all()
        for item in queryset:
            if item.hydrologic_region_slug == None:
                parent_obj = WaterSupplier.objects.get(supplier_name = item.supplier_name_id)
                item.hydrologic_region_slug = self._slug_a_string(item.hydrologic_region)
                logger.debug(item.hydrologic_region_slug)
                item.save()
            else:
                logger.debug("Everything's cool!")

    def add_supplier_slug_to_watersuppliermonthlyreport(self):
        queryset = WaterSupplierMonthlyReport.objects.all()
        for item in queryset:
            if item.supplier_slug == None:
                item.supplier_slug = self._slug_a_string(item.supplier_name_id)
                logger.debug(item.supplier_slug)
                #item.save()
            else:
                logger.debug("Everything's cool!")

    def fix_dates_on_reports(self):
        queryset = WaterSupplierMonthlyReport.objects.filter(report_date = "2015-04-07")
        for item in queryset:
            output = datetime.date(item.reporting_month.year, item.reporting_month.month, 01)
            item.reporting_month = output
            logger.debug(item.reporting_month)
            item.save()

    def model_first_and_second_reduction_proposals(self):
        suppliers = WaterSupplier.objects.all()
        queryset = WaterSupplierMonthlyReport.objects.filter(report_date = "2015-04-07")
        new_queries = QueryUtilities()
        all_months_latest_report = new_queries._all_months_latest_report(queryset)
        for supplier in suppliers:
            results = all_months_latest_report.filter(supplier_name_id = supplier.supplier_name)
            this_supplier_set = results.filter(Q(reporting_month = "2014-07-01") | Q(reporting_month = "2014-08-01") | Q(reporting_month = "2014-09-01"))
            if len(this_supplier_set) > 0:
                three_month_rgcpd = new_queries._get_rolling_avg_rgcpd(this_supplier_set)
            else:
                three_month_rgcpd = None
            april_7_tier = new_queries._get_conservation_tier(this_supplier_set)
            april_18_tier = new_queries._get_second_draft_conservation_tier(three_month_rgcpd)
            supplier.april_7_tier = april_7_tier["conservation_tier"]
            supplier.april_7_reduction = april_7_tier["conservation_standard"]
            supplier.april_7_rgpcd = april_7_tier["conservation_placement"]
            supplier.april_18_tier = april_18_tier["conservation_tier"]
            supplier.april_18_reduction = april_18_tier["conservation_standard"]
            supplier.april_18_rgpcd = april_18_tier["conservation_placement"]
            supplier.save()

    def model_third_reduction_proposals(self, created_csv_file):
        sluggy = BuildMonthlyWaterUseReport()
        with open(created_csv_file, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:
                as_decimal = row["conservation_standard"].replace("%", "")
                as_decimal = int(as_decimal) / 100
                rgpcd = float(row["jul_sep_2014_rgpcd"])
                supplier_formal = sluggy._prettify_and_slugify(row["supplier_name"])
                if supplier_formal[0] != None:
                    supplier = WaterSupplier.objects.filter(supplier_slug = supplier_formal[0])
                    for item in supplier:
                        item.april_28_tier = row["tier"]
                        item.april_28_reduction = as_decimal
                        item.april_28_rgpcd = row["jul_sep_2014_rgpcd"]
                        item.save()

    def model_monthly_enforcement_stats(self, created_csv_file):
        sluggy = BuildMonthlyWaterUseReport()
        with open(created_csv_file, "rb") as csvfile:
            csv_data = csv.DictReader(csvfile, delimiter=',')
            for row in csv_data:

                report_date = datetime.date(2015, 05, 05)

                parsed_date = parser.parse(row["DateTime"])
                reported_to_state_date = datetime.date(parsed_date.year, parsed_date.month, parsed_date.day)

                reporting_month = datetime.date(2015, 03, 03)

                supplier_formal = sluggy._prettify_and_slugify(row["Supplier Name"])
                supplier_slug = supplier_formal[0]
                supplier_name = supplier_formal[1]

                hydrologic_region = row["Hydrologic Region"]

                hydrologic_region_slug = self._slug_a_string(hydrologic_region)

                enforcement_comments = row["Enforcement Comments"]

                mandatory_restrictions = row["Mandatory Restrictions"]

                total_population_served = row["Population Served"]

                supplier_id = row["Supplier"]

                try:
                    water_days_allowed_week = int(row["Water Days Allowed/Week"])
                except Exception, exception:
                    if row["Water Days Allowed/Week"] == "":
                        water_days_allowed_week = None
                    print "%s - %s" % (exception, row)

                try:
                    complaints_received = int(row["Complaints Received"])
                except Exception, exception:
                    if row["Complaints Received"] == "":
                        complaints_received = None
                    print "%s - %s" % (exception, row)

                try:
                    penalties_assessed = int(row["Penalties Assessed"])
                except Exception, exception:
                    if row["Penalties Assessed"] == "":
                        penalties_assessed = None
                    print "%s - %s" % (exception, row)

                try:
                    follow_up_actions = int(row["Follow-up Actions"])
                except Exception, exception:
                    if row["Follow-up Actions"] == "":
                        follow_up_actions = None
                    print "%s - %s" % (exception, row)

                try:
                    warnings_issued = int(row["Warnings Issued"])
                except Exception, exception:
                    if row["Warnings Issued"] == "":
                        warnings_issued = None
                    print "%s - %s" % (exception, row)

                try:
                    obj, created = WaterEnforcementMonthlyReport.objects.get_or_create(
                        report_date = report_date,
                        supplier_name = supplier_name,
                        reporting_month = reporting_month,
                        defaults = {
                            "reported_to_state_date": reported_to_state_date,
                            "supplier_slug": supplier_slug,
                            "hydrologic_region": hydrologic_region,
                            "hydrologic_region_slug": hydrologic_region_slug,
                            "enforcement_comments": enforcement_comments,
                            "water_days_allowed_week": water_days_allowed_week,
                            "complaints_received": complaints_received,
                            "mandatory_restrictions": mandatory_restrictions,
                            "total_population_served": total_population_served,
                            "supplier_id": supplier_id,
                            "penalties_assessed": penalties_assessed,
                            "follow_up_actions": follow_up_actions,
                            "warnings_issued": warnings_issued,
                        }
                    )
                    if not created:
                        logger.debug("%s - %s exists" % (supplier_name, reporting_month))
                    elif created:
                        logger.debug("%s - %s created" % (supplier_name, reporting_month))
                except ObjectDoesNotExist, exception:
                    logger.error("%s %s" % (exception, supplier_slug))

    def _slug_a_string(self, string):
        value = string.encode("ascii", "ignore").lower().strip().replace(" ", "-")
        value = re.sub(r"[^\w-]", "", value)
        return value

if __name__ == '__main__':
    task_run = TasksForMonthlyWaterUseReport()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
