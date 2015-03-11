from __future__ import division
from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View, ListView, DetailView
from django.db.models import Q, Avg, Max, Min, Sum, Count
from cali_water.models import WaterSupplier, WaterSupplierMonthlyReport, WaterIncentive, WaterRestriction, WaterConservationMethod
from bakery.views import BuildableListView, BuildableDetailView
import datetime
import logging
import yaml

logger = logging.getLogger("accountability_tracker")

# Create your views here.
class InitialListView(BuildableListView):

    model = WaterSupplierMonthlyReport
    template_name = "cali_water/index.html"

    def get_object(self):
        object = super(InitialListView, self).get_object()
        return object

    def get_queryset(self):
        queryset = super(InitialListView, self).get_queryset()

        latest_data = queryset.aggregate(Max("reporting_month"))

        logger.debug(latest_data)

        latest_report_date = queryset.aggregate(Max("report_date"))

        target_report = datetime.date(latest_data["reporting_month__max"].year, latest_data["reporting_month__max"].month, latest_data["reporting_month__max"].day)

        supplier_reports = queryset.filter(supplier_name_id__hydrologic_region = "South Coast").filter(report_date = latest_report_date["report_date__max"]).filter(reporting_month__gte = target_report).extra(select = {"percent_change": "((calculated_rgpcd_2014-calculated_rgpcd_2013)/calculated_rgpcd_2013)*100"})

        option_list = WaterSupplier.objects.values("hydrologic_region").distinct()

        for item in option_list:
            item["suppliers"] = WaterSupplier.objects.filter(hydrologic_region = item["hydrologic_region"]).order_by("supplier_name")

        largest_increase = supplier_reports.order_by("-percent_change")[:5]

        largest_decrease = supplier_reports.order_by("percent_change")[:5]

        # https://github.com/censusreporter/censusreporter/blob/47ee559d3939ec00d2e39e1f540b277bc50bbff8/censusreporter/apps/census/static/js/comparisons.js#L703
        count = supplier_reports.count()

        median_results = supplier_reports.values_list("percent_change", flat=True).order_by("percent_change")[int(round(count/2))]

        values_range = largest_increase[0].percent_change - largest_decrease[0].percent_change

        config = yaml.load(open("cali_water/config.yml"))

        return {
            "article_content": config["article_content"],
            "about_content": config["about_content"],
            "config_object": config["config_object"],
            "option_list": option_list,
            "target_report": target_report,
            "largest_increase": largest_increase,
            "largest_decrease": largest_decrease,
            "median_results": median_results
        }

class InitialDetailView(BuildableDetailView):
    model = WaterSupplier
    template_name = "cali_water/detail.html"
    slug_field = "supplier_slug"

    def get_object(self):
        object = super(InitialDetailView, self).get_object()
        return object

    def get_context_data(self, **kwargs):

        config = yaml.load(open("cali_water/config.yml"))

        context = super(InitialDetailView, self).get_context_data(**kwargs)

        context["slug"] = self.object.supplier_slug

        context["article_content"] = config["article_content"]

        context["about_content"] = config["about_content"]

        context["config_object"] = config["config_object"]

        latest_report_date = WaterSupplierMonthlyReport.objects.aggregate(Max("report_date"))

        results = WaterSupplierMonthlyReport.objects.filter(supplier_name_id = self.object).filter(report_date = latest_report_date["report_date__max"]).order_by("-reporting_month")

        context["results"] = results

        context["avg_rgcpd_2014"] = self._rolling_avg_rgcpd(results)

        context["restrictions"] = WaterRestriction.objects.filter(supplier_name_id = self.object)

        context["incentives"] = WaterIncentive.objects.filter(supplier_name_id = self.object)

        context["conservation_methods"] = WaterConservationMethod.objects.all().order_by("?")[:4]

        context["labels"] = []

        context["data_2014"] = []

        #context["data_2013"] = []

        for result in context["results"]:
            month_label = result.reporting_month.strftime("%b %Y")
            context["labels"].append(month_label)
            context["data_2014"].append(result.calculated_rgpcd_2014)
            #context["data_2013"].append(result.calculated_rgpcd_2013)

        context["labels"] = context["labels"]
        context["data_2014"] = context["data_2014"]
        #context["data_2013"] = context["data_2013"]

        return context

    def _rolling_avg_rgcpd(self, results):
        days = [30, 31, 31, 30, 31, 30, 31]

        tmp = []

        pru = []

        tps = []

        for result in results:

            if result.units == "G":
                tmp.append(1 * result.total_monthly_potable_water_production_2014)

            elif result.units == "MG":
                tmp.append(1000000 * result.total_monthly_potable_water_production_2014)

            elif result.units == "CCF":
                tmp.append(748 * result.total_monthly_potable_water_production_2014)

            elif result.units == "AF":
                tmp.append(325851 * result.total_monthly_potable_water_production_2014)

            pru.append(result.percent_residential_use)

            tps.append(result.total_population_served)

        avg_tmp = sum(tmp) / float(len(tmp))

        avg_pru = sum(pru) / float(len(pru))

        avg_tps = sum(tps) / float(len(tps))

        avg_days = sum(days) / float(len(days))

        avg_rgcpd = ((avg_tmp * avg_pru) / avg_tps) / avg_days

        return avg_rgcpd
