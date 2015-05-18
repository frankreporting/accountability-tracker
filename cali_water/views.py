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
from cali_water.models import WaterSupplier, WaterSupplierMonthlyReport, WaterEnforcementMonthlyReport, WaterIncentive, WaterRestriction, WaterConservationMethod, HydrologicRegion
from bakery.views import BuildableListView, BuildableDetailView
import os
import calculate
import datetime
import logging
import yaml
import calendar

logger = logging.getLogger("accountability_tracker")

# Create your views here.
class InitialIndex(BuildableListView):

    model = WaterSupplierMonthlyReport

    template_name = "cali_water/index.html"

    def get_object(self):
        object = super(InitialIndex, self).get_object()
        return object

    def get_queryset(self):

        # grab the yaml configuration items
        config = yaml.load(open("cali_water/config.yml"))

        # get all the reports
        queryset = super(InitialIndex, self).get_queryset()

        # get all of the water suppliers
        water_suppliers = WaterSupplier.objects.all()

        new_queries = QueryUtilities()

        # get queryset of the latest month from the most recent report
        latest_month_latest_report = new_queries._latest_month_latest_report(queryset)

        # get the most recent data from the most recent report
        all_months_latest_report = new_queries._all_months_latest_report(queryset)

        # get a queryset of the months represented in the database
        months_in_report = all_months_latest_report.exclude(reporting_month__isnull=True).values("reporting_month").distinct().order_by("-reporting_month")

        # get the max value of calculated_rgpcd_2014 in the latest report
        global_max = latest_month_latest_report.values("calculated_rgpcd_2014").aggregate(Max("calculated_rgpcd_2014"))

        # get the min value of calculated_rgpcd_2014 in the latest report
        global_min = latest_month_latest_report.values("calculated_rgpcd_2014").aggregate(Min("calculated_rgpcd_2014"))

        # create the hydrologic_region option list
        hydrologic_regions = water_suppliers.exclude(hydrologic_region__isnull=True).values("hydrologic_region").distinct()

        for item in hydrologic_regions:
            item["suppliers"] = water_suppliers.filter(hydrologic_region = item["hydrologic_region"]).order_by("supplier_name")

        # create the hydrologic_region data for the maps
        map_data = water_suppliers.exclude(hydrologic_region__isnull=True).values("hydrologic_region").distinct()

        for item in map_data:
            this_month = all_months_latest_report.filter(hydrologic_region = item["hydrologic_region"]).filter(reporting_month = months_in_report[0]["reporting_month"])
            this_month_avg = new_queries._get_avg_rgcpd(this_month)
            item["this_month_avg"] = this_month_avg

            this_month_baseline_avg = new_queries._get_last_year_avg_rgcpd(this_month)
            item["this_month_baseline_avg"] = this_month_baseline_avg

            last_month = all_months_latest_report.filter(hydrologic_region = item["hydrologic_region"]).filter(reporting_month = months_in_report[1]["reporting_month"])
            last_month_avg = new_queries._get_avg_rgcpd(last_month)
            item["last_month_avg"] = last_month_avg

            item["suppliers"] = list(latest_month_latest_report.filter(hydrologic_region = item["hydrologic_region"]).values("supplier_name", "calculated_rgpcd_2014").order_by("calculated_rgpcd_2014"))

            item["count"] = latest_month_latest_report.filter(hydrologic_region = item["hydrologic_region"]).count()

            item["this_max"] = latest_month_latest_report.filter(hydrologic_region = item["hydrologic_region"]).values("calculated_rgpcd_2014").aggregate(Max("calculated_rgpcd_2014"))

            item["this_min"] = latest_month_latest_report.filter(hydrologic_region = item["hydrologic_region"]).values("calculated_rgpcd_2014").aggregate(Min("calculated_rgpcd_2014"))

            item["median"] =  latest_month_latest_report.filter(hydrologic_region = item["hydrologic_region"]).values_list("calculated_rgpcd_2014", flat=True).order_by("calculated_rgpcd_2014")[int(round(item["count"]/2))]

            item["min_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_min"]["calculated_rgpcd_2014__min"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

            item["max_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_max"]["calculated_rgpcd_2014__max"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

            item["median_range"] = new_queries.pct_value_inside_arbitrary_range(item["median"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

            item["average_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_month_avg"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

            for supplier in item["suppliers"]:
                supplier["distribution_precent"] = new_queries.pct_value_inside_arbitrary_range(supplier["calculated_rgpcd_2014"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        # calculate the state average rgcpd for the current month
        state_this_month = all_months_latest_report.filter(reporting_month = months_in_report[0]["reporting_month"])
        state_avg_latest = new_queries._get_avg_rgcpd(state_this_month)

        # calculate the state average rgcpd for last month
        state_last_month = all_months_latest_report.filter(reporting_month = months_in_report[1]["reporting_month"])
        state_avg_last = new_queries._get_avg_rgcpd(state_last_month)

        return {
            "article_content": config["article_content"],
            "about_content": config["about_content"],
            "config_object": config["config_object"],
            "target_report": latest_month_latest_report[0].reporting_month,
            "option_list": hydrologic_regions,
            "map_data": list(map_data),
            "global_max": global_max,
            "global_min": global_min,
            "state_avg_latest": state_avg_latest,
            "state_avg_last": state_avg_last,
        }


class ComparisonIndex(BuildableDetailView):

    model = HydrologicRegion

    template_name = "cali_water/region_reduction_comparison.html"

    slug_field = "hydrologic_region_slug"

    sub_directory = "region/"

    def get_object(self):
        object = super(ComparisonIndex, self).get_object()
        return object

    def get_build_path(self, obj):
        """
        used to determine where to build the detail page. override this if you
        would like your detail page at a different location. by default it
        will be built at get_url() + "index.html"
        """
        path = os.path.join(settings.BUILD_DIR, self.sub_directory, self.get_url(obj)[1:])
        path = "%sreduction-comparison/" % (path)
        os.path.exists(path) or os.makedirs(path)
        return os.path.join(path, "index.html")

    def get_context_data(self, **kwargs):

        # grab the yaml configuration items
        config = yaml.load(open("cali_water/config.yml"))

        # create the context object
        context = super(ComparisonIndex, self).get_context_data(**kwargs)

        # add the article content config to the context
        context["article_content"] = config["article_content"]

        # add the about this to the context
        context["about_content"] = config["about_content"]

        # add the javascript config to the context
        context["config_object"] = config["config_object"]

        # get the supplier slug
        context["region_slug"] = self.object.hydrologic_region_slug

        # get the supplier slug
        context["region_name"] = self.object.hydrologic_region

        # get all the reports
        queryset = WaterSupplierMonthlyReport.objects.all()

        # get all of the water suppliers
        water_suppliers = WaterSupplier.objects.all().filter(hydrologic_region = context["region_name"]).order_by("hydrologic_region", "supplier_name")

        new_queries = QueryUtilities()

        # get queryset of the latest month from the most recent report
        latest_month_latest_report = new_queries._latest_month_latest_report(queryset)

        # get the most recent data from the most recent report
        all_months_latest_report = new_queries._all_months_latest_report(queryset)

        context["target_report"] = latest_month_latest_report[0].reporting_month

        context["water_suppliers"] = water_suppliers

        return context


class EnforcementIndex(BuildableDetailView):

    model = HydrologicRegion

    template_name = "cali_water/region_enforcement_comparison.html"

    slug_field = "hydrologic_region_slug"

    sub_directory = "region/"

    def get_object(self):
        object = super(EnforcementIndex, self).get_object()
        return object

    def get_build_path(self, obj):
        """
        used to determine where to build the detail page. override this if you
        would like your detail page at a different location. by default it
        will be built at get_url() + "index.html"
        """
        path = os.path.join(settings.BUILD_DIR, self.sub_directory, self.get_url(obj)[1:])
        path = "%senforcement-comparison/" % (path)
        os.path.exists(path) or os.makedirs(path)
        return os.path.join(path, "index.html")

    def get_context_data(self, **kwargs):

        # grab the yaml configuration items
        config = yaml.load(open("cali_water/config.yml"))

        # create the context object
        context = super(EnforcementIndex, self).get_context_data(**kwargs)

        # add the article content config to the context
        context["article_content"] = config["article_content"]

        # add the about this to the context
        context["about_content"] = config["about_content"]

        # add the javascript config to the context
        context["config_object"] = config["config_object"]

        # get the supplier slug
        context["region_slug"] = self.object.hydrologic_region_slug

        # get the supplier slug
        context["region_name"] = self.object.hydrologic_region

        # get all the reports
        queryset = WaterEnforcementMonthlyReport.objects.filter(hydrologic_region = context["region_name"]).order_by("hydrologic_region", "supplier_name")

        new_queries = QueryUtilities()

        # get queryset of the latest month from the most recent report
        latest_month_latest_report = new_queries._latest_month_latest_report(queryset)

        context["target_report"] = latest_month_latest_report[0].reporting_month

        context["water_suppliers"] = queryset

        return context


class RegionDetailView(BuildableDetailView):

    model = HydrologicRegion

    template_name = "cali_water/region_detail.html"

    slug_field = "hydrologic_region_slug"

    sub_directory = "region/"

    def get_object(self):
        object = super(RegionDetailView, self).get_object()
        return object

    def get_build_path(self, obj):
        """
        used to determine where to build the detail page. override this if you
        would like your detail page at a different location. by default it
        will be built at get_url() + "index.html"
        """
        path = os.path.join(settings.BUILD_DIR, self.sub_directory, self.get_url(obj)[1:])
        os.path.exists(path) or os.makedirs(path)
        return os.path.join(path, "index.html")

    def get_context_data(self, **kwargs):

        # grab the yaml configuration items
        config = yaml.load(open("cali_water/config.yml"))

        # create the context object
        context = super(RegionDetailView, self).get_context_data(**kwargs)

        # add the article content config to the context
        context["article_content"] = config["article_content"]

        # add the about this to the context
        context["about_content"] = config["about_content"]

        # add the javascript config to the context
        context["config_object"] = config["config_object"]

        # get the supplier slug
        context["region_slug"] = self.object.hydrologic_region_slug

        # get the supplier slug
        context["region_name"] = self.object.hydrologic_region

        # get a queryset for this hydrologic region
        queryset = WaterSupplierMonthlyReport.objects.filter(hydrologic_region = context["region_name"]).order_by("supplier_name_id")

        # new instance of the utility class
        new_queries = QueryUtilities()

        # get queryset of the latest month from the most recent report
        latest_month_latest_report = new_queries._latest_month_latest_report(queryset)

        # get the most recent month of data from the most recent report
        all_months_latest_report = new_queries._all_months_latest_report(queryset)

        # get the most recent data for all the months in the most recent report
        months_in_report = all_months_latest_report.exclude(reporting_month__isnull=True).values("reporting_month").distinct().order_by("-reporting_month")

        # get the max value of calculated_rgpcd_2014 in the latest report
        global_max = latest_month_latest_report.values("calculated_rgpcd_2014").aggregate(Max("calculated_rgpcd_2014"))

        # assign it to context
        context["global_max"] = global_max

        # get the min value of calculated_rgpcd_2014 in the latest report
        global_min = latest_month_latest_report.values("calculated_rgpcd_2014").aggregate(Min("calculated_rgpcd_2014"))

        # assign it to context
        context["global_min"] = global_min

        context["target_report"] = latest_month_latest_report[0].reporting_month

        context["reports_from_region"] = latest_month_latest_report

        # create the hydrologic_region data for the maps
        map_data = []

        item = {}

        item["hydrologic_slug"] = context["region_slug"]

        item["hydrologic_region"] = context["region_name"]

        # create the hydrologic_region data for the maps
        this_month = all_months_latest_report.filter(hydrologic_region = context["region_name"]).filter(reporting_month = months_in_report[0]["reporting_month"])
        this_month_avg = new_queries._get_avg_rgcpd(this_month)
        item["this_month_avg"] = this_month_avg

        this_month_baseline_avg = new_queries._get_last_year_avg_rgcpd(this_month)
        item["this_month_baseline_avg"] = this_month_baseline_avg

        last_month = all_months_latest_report.filter(hydrologic_region = context["region_name"]).filter(reporting_month = months_in_report[1]["reporting_month"])
        last_month_avg = new_queries._get_avg_rgcpd(last_month)
        item["last_month_avg"] = last_month_avg

        item["suppliers"] = list(latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values("supplier_name", "calculated_rgpcd_2014").order_by("supplier_name_id", "calculated_rgpcd_2014"))

        item["count"] = latest_month_latest_report.filter(hydrologic_region = context["region_name"]).count()

        item["this_max"] = latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values("calculated_rgpcd_2014").aggregate(Max("calculated_rgpcd_2014"))

        item["this_min"] = latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values("calculated_rgpcd_2014").aggregate(Min("calculated_rgpcd_2014"))

        item["median"] =  latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values_list("calculated_rgpcd_2014", flat=True).order_by("calculated_rgpcd_2014")[int(round(item["count"]/2))]

        item["min_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_min"]["calculated_rgpcd_2014__min"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        item["max_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_max"]["calculated_rgpcd_2014__max"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        item["median_range"] = new_queries.pct_value_inside_arbitrary_range(item["median"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        item["average_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_month_avg"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        for supplier in item["suppliers"]:
            supplier["distribution_precent"] = new_queries.pct_value_inside_arbitrary_range(supplier["calculated_rgpcd_2014"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        map_data.append(item)

        context["map_data"] = map_data

        return context


class RegionEmbedView(BuildableDetailView):

    model = HydrologicRegion

    template_name = "cali_water/region_embed.html"

    slug_field = "hydrologic_region_slug"

    sub_directory = "share/"

    def get_object(self):
        object = super(RegionEmbedView, self).get_object()
        return object

    def get_build_path(self, obj):
        """
        used to determine where to build the detail page. override this if you
        would like your detail page at a different location. by default it
        will be built at get_url() + "index.html"
        """
        path = os.path.join(settings.BUILD_DIR, self.sub_directory, self.get_url(obj)[1:])
        os.path.exists(path) or os.makedirs(path)
        return os.path.join(path, "index.html")

    def get_context_data(self, **kwargs):

        # grab the yaml configuration items
        config = yaml.load(open("cali_water/config.yml"))

        # create the context object
        context = super(RegionEmbedView, self).get_context_data(**kwargs)

        # add the article content config to the context
        context["article_content"] = config["article_content"]

        # add the about this to the context
        context["about_content"] = config["about_content"]

        # add the javascript config to the context
        context["config_object"] = config["config_object"]

        # get the supplier slug
        context["region_slug"] = self.object.hydrologic_region_slug

        # get the supplier slug
        context["region_name"] = self.object.hydrologic_region

        # get a queryset for this hydrologic region
        queryset = WaterSupplierMonthlyReport.objects.filter(hydrologic_region = context["region_name"]).order_by("supplier_name_id")

        # new instance of the utility class
        new_queries = QueryUtilities()

        # get queryset of the latest month from the most recent report
        latest_month_latest_report = new_queries._latest_month_latest_report(queryset)

        # get the most recent month of data from the most recent report
        all_months_latest_report = new_queries._all_months_latest_report(queryset)

        # get the most recent data for all the months in the most recent report
        months_in_report = all_months_latest_report.exclude(reporting_month__isnull=True).values("reporting_month").distinct().order_by("-reporting_month")

        # get the max value of calculated_rgpcd_2014 in the latest report
        global_max = latest_month_latest_report.values("calculated_rgpcd_2014").aggregate(Max("calculated_rgpcd_2014"))

        # assign it to context
        context["global_max"] = global_max

        # get the min value of calculated_rgpcd_2014 in the latest report
        global_min = latest_month_latest_report.values("calculated_rgpcd_2014").aggregate(Min("calculated_rgpcd_2014"))

        # assign it to context
        context["global_min"] = global_min

        context["target_report"] = latest_month_latest_report[0].reporting_month

        context["reports_from_region"] = latest_month_latest_report

        # create the hydrologic_region data for the maps
        map_data = []

        item = {}

        item["hydrologic_slug"] = context["region_slug"]

        item["hydrologic_region"] = context["region_name"]

        # create the hydrologic_region data for the maps
        this_month = all_months_latest_report.filter(hydrologic_region = context["region_name"]).filter(reporting_month = months_in_report[0]["reporting_month"])
        this_month_avg = new_queries._get_avg_rgcpd(this_month)
        item["this_month_avg"] = this_month_avg

        this_month_baseline_avg = new_queries._get_last_year_avg_rgcpd(this_month)
        item["this_month_baseline_avg"] = this_month_baseline_avg

        last_month = all_months_latest_report.filter(hydrologic_region = context["region_name"]).filter(reporting_month = months_in_report[1]["reporting_month"])
        last_month_avg = new_queries._get_avg_rgcpd(last_month)
        item["last_month_avg"] = last_month_avg

        item["suppliers"] = list(latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values("supplier_name", "calculated_rgpcd_2014").order_by("supplier_name_id", "calculated_rgpcd_2014"))

        item["count"] = latest_month_latest_report.filter(hydrologic_region = context["region_name"]).count()

        item["this_max"] = latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values("calculated_rgpcd_2014").aggregate(Max("calculated_rgpcd_2014"))

        item["this_min"] = latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values("calculated_rgpcd_2014").aggregate(Min("calculated_rgpcd_2014"))

        item["median"] =  latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values_list("calculated_rgpcd_2014", flat=True).order_by("calculated_rgpcd_2014")[int(round(item["count"]/2))]

        item["min_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_min"]["calculated_rgpcd_2014__min"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        item["max_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_max"]["calculated_rgpcd_2014__max"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        item["median_range"] = new_queries.pct_value_inside_arbitrary_range(item["median"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        item["average_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_month_avg"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        for supplier in item["suppliers"]:
            supplier["distribution_precent"] = new_queries.pct_value_inside_arbitrary_range(supplier["calculated_rgpcd_2014"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        map_data.append(item)

        context["map_data"] = map_data

        return context


class RegionReportView(BuildableDetailView):

    model = HydrologicRegion

    template_name = "cali_water/region_report.html"

    slug_field = "hydrologic_region_slug"

    sub_directory = "region/"

    def get_object(self):
        object = super(RegionReportView, self).get_object()
        return object

    def get_build_path(self, obj):
        """
        used to determine where to build the detail page. override this if you
        would like your detail page at a different location. by default it
        will be built at get_url() + "index.html"
        """
        path = os.path.join(settings.BUILD_DIR, self.sub_directory, self.get_url(obj)[1:])
        path = "%sreport/" % (path)
        os.path.exists(path) or os.makedirs(path)
        return os.path.join(path, "index.html")

    def get_context_data(self, **kwargs):

        # grab the yaml configuration items
        config = yaml.load(open("cali_water/config.yml"))

        # create the context object
        context = super(RegionReportView, self).get_context_data(**kwargs)

        # add the article content config to the context
        context["article_content"] = config["article_content"]

        # add the about this to the context
        context["about_content"] = config["about_content"]

        # add the javascript config to the context
        context["config_object"] = config["config_object"]

        # get the supplier slug
        context["region_slug"] = self.object.hydrologic_region_slug

        # get the supplier slug
        context["region_name"] = self.object.hydrologic_region

        # get a queryset for this hydrologic region
        queryset = WaterSupplierMonthlyReport.objects.filter(hydrologic_region = context["region_name"]).order_by("supplier_name_id")

        # new instance of the utility class
        new_queries = QueryUtilities()

        # get queryset of the latest month from the most recent report
        latest_month_latest_report = new_queries._latest_month_latest_report(queryset)

        # get the most recent month of data from the most recent report
        all_months_latest_report = new_queries._all_months_latest_report(queryset)

        # get the most recent data for all the months in the most recent report
        months_in_report = all_months_latest_report.exclude(reporting_month__isnull=True).values("reporting_month").distinct().order_by("-reporting_month")

        # get the max value of calculated_rgpcd_2014 in the latest report
        global_max = latest_month_latest_report.values("calculated_rgpcd_2014").aggregate(Max("calculated_rgpcd_2014"))

        # assign it to context
        context["global_max"] = global_max

        # get the min value of calculated_rgpcd_2014 in the latest report
        global_min = latest_month_latest_report.values("calculated_rgpcd_2014").aggregate(Min("calculated_rgpcd_2014"))

        # assign it to context
        context["global_min"] = global_min

        context["target_report"] = latest_month_latest_report[0].reporting_month

        context["reports_from_region"] = latest_month_latest_report

        # create the hydrologic_region data for the maps
        map_data = []

        item = {}

        item["hydrologic_slug"] = context["region_slug"]

        item["hydrologic_region"] = context["region_name"]

        # create the hydrologic_region data for the maps
        this_month = all_months_latest_report.filter(hydrologic_region = context["region_name"]).filter(reporting_month = months_in_report[0]["reporting_month"])
        this_month_avg = new_queries._get_avg_rgcpd(this_month)
        item["this_month_avg"] = this_month_avg

        this_month_baseline_avg = new_queries._get_last_year_avg_rgcpd(this_month)
        item["this_month_baseline_avg"] = this_month_baseline_avg

        last_month = all_months_latest_report.filter(hydrologic_region = context["region_name"]).filter(reporting_month = months_in_report[1]["reporting_month"])
        last_month_avg = new_queries._get_avg_rgcpd(last_month)
        item["last_month_avg"] = last_month_avg

        item["suppliers"] = list(latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values("supplier_name", "supplier_slug", "calculated_rgpcd_2013", "calculated_rgpcd_2014").order_by("supplier_name_id", "calculated_rgpcd_2013", "calculated_rgpcd_2014"))

        item["count"] = latest_month_latest_report.filter(hydrologic_region = context["region_name"]).count()

        item["this_max"] = latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values("calculated_rgpcd_2014").aggregate(Max("calculated_rgpcd_2014"))

        item["this_min"] = latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values("calculated_rgpcd_2014").aggregate(Min("calculated_rgpcd_2014"))

        item["median"] =  latest_month_latest_report.filter(hydrologic_region = context["region_name"]).values_list("calculated_rgpcd_2014", flat=True).order_by("calculated_rgpcd_2014")[int(round(item["count"]/2))]

        item["min_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_min"]["calculated_rgpcd_2014__min"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        item["max_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_max"]["calculated_rgpcd_2014__max"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        item["median_range"] = new_queries.pct_value_inside_arbitrary_range(item["median"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        item["average_range"] = new_queries.pct_value_inside_arbitrary_range(item["this_month_avg"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        for supplier in item["suppliers"]:
            supplier["distribution_precent"] = new_queries.pct_value_inside_arbitrary_range(supplier["calculated_rgpcd_2014"], global_min["calculated_rgpcd_2014__min"], global_max["calculated_rgpcd_2014__max"])

        map_data.append(item)

        context["map_data"] = map_data

        return context








class SupplierDetailView(BuildableDetailView):

    model = WaterSupplier

    template_name = "cali_water/supplier_detail.html"

    slug_field = "supplier_slug"

    def get_object(self):
        object = super(SupplierDetailView, self).get_object()
        return object

    #def get_build_path(self, obj):
        """
        used to determine where to build the detail page. override this if you
        would like your detail page at a different location. by default it
        will be built at get_url() + "index.html"
        """
        #path = os.path.join(settings.BUILD_DIR, self.sub_directory, self.get_url(obj)[1:])
        #os.path.exists(path) or os.makedirs(path)
        #return os.path.join(path, "index.html")

    def get_context_data(self, **kwargs):

        # grab the yaml configuration items
        config = yaml.load(open("cali_water/config.yml"))

        # create the context object
        context = super(SupplierDetailView, self).get_context_data(**kwargs)

        # add the article content config to the context
        context["article_content"] = config["article_content"]

        # add the about this to the context
        context["about_content"] = config["about_content"]

        # add the javascript config to the context
        context["config_object"] = config["config_object"]

        # get the supplier slug
        context["slug"] = self.object.supplier_slug

        # get all the reports
        queryset = WaterSupplierMonthlyReport.objects.all()

        # create instance of query class
        new_queries = QueryUtilities()

        # get queryset of the latest month from the most recent report
        latest_month_latest_report = new_queries._latest_month_latest_report(queryset)

        # calculate & return the state average rgcpd for the current month
        context["latest_state_avg"] = new_queries._get_avg_rgcpd(latest_month_latest_report)

        # get & return queryset of all the months from the most recent report
        all_months_latest_report = new_queries._all_months_latest_report(queryset)

        context["results"] = all_months_latest_report.filter(supplier_name_id = self.object)

        context["april_7_tier"] = {
            "conservation_standard": self.object.april_7_reduction,
            "conservation_placement": self.object.april_7_rgpcd,
            "conservation_tier": self.object.april_7_tier,
        }

        context["april_18_tier"] = {
            "conservation_standard": self.object.april_18_reduction,
            "conservation_placement": self.object.april_18_rgpcd,
            "conservation_tier": self.object.april_18_tier,
        }

        context["april_28_tier"] = {
            "conservation_standard": self.object.april_28_reduction,
            "conservation_placement": self.object.april_28_rgpcd,
            "conservation_tier": self.object.april_28_tier,
        }

        """
        used to calculate reduction tier and has since been saved to the model
        """
        #this_supplier_set = context["results"].filter(Q(reporting_month = "2014-07-01") | Q(reporting_month = "2014-08-01") | Q(reporting_month = "2014-09-01"))

        #if len(this_supplier_set) > 0:
            #three_month_rgcpd = new_queries._get_rolling_avg_rgcpd(this_supplier_set)
        #else:
            #three_month_rgcpd = None

        #context["first_draft_tier"] = new_queries._get_conservation_tier(this_supplier_set)

        #context["second_draft_tier"] = new_queries._get_second_draft_conservation_tier(three_month_rgcpd)

        # return the conservation standard
        #context["conservation"] = new_queries._get_conservation_tier(context["results"])

        # return the restrictions if present
        context["restrictions"] = WaterRestriction.objects.filter(supplier_name_id = self.object)

        # return the incentives if present
        context["incentives"] = WaterIncentive.objects.filter(supplier_name_id = self.object)

        # return the conservation_methods if present
        context["conservation_methods"] = WaterConservationMethod.objects.all().order_by("?")[:4]

        context["target_report"] = latest_month_latest_report[0].reporting_month

        # create the lists needed for the chart
        context["labels"] = []
        context["data_2014"] = []
        context["data_2013"] = []

        # append data to the lists for the chart
        for result in context["results"]:
            month_label = result.reporting_month.strftime("%b")
            context["labels"].append(month_label)
            context["data_2014"].append(result.calculated_rgpcd_2014)
            context["data_2013"].append(result.calculated_rgpcd_2013)

        # return the context
        return context

class QueryUtilities(object):


    # get me the latest south coast supplier reports
    #local_supplier_reports = current_data.filter(supplier_name_id__hydrologic_region = "South Coast").extra(select = {"percent_change": "((calculated_rgpcd_2014-calculated_rgpcd_2013)/calculated_rgpcd_2013)*100"})

    # show which agencies increased & decreased residential gallons per capita day
    #largest_increase = local_supplier_reports.order_by("-percent_change")[:5]
    #largest_decrease = local_supplier_reports.order_by("percent_change")[:5]

    # misc calculations
    #http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/emergency_regulations/urban_water_supplier_tiers.pdf


    # https://latimes-calculate.readthedocs.org/en/latest/basicfunctions.html#at-percentile
    # https://latimes-calculate.readthedocs.org/en/latest/basicfunctions.html#percentile
    # https://latimes-calculate.readthedocs.org/en/latest/basicfunctions.html#ordinal-rank

    # http://www.nytimes.com/interactive/2015/04/01/us/water-use-in-california.html?mabReward=A4&action=click&pgtype=Homepage&region=CColumn&module=Recommendation&src=rechp&WT.nav=RecEngine&_r=2
    # http://www2.pacinst.org/gpcd/table.html#

    # http://www.waterboards.ca.gov/press_room/press_releases/2015/pr030315_urbanwater.pdf

    #parent_obj = WaterSupplier.objects.values_list("hydrologic_region").distinct()

    #logger.debug(parent_obj)

    #for item in results:
        #parent_obj = WaterSupplier.objects.get(supplier_name = item.supplier_name_id)
        #logger.debug(parent_obj.hydrologic_region)

    # determine aggregate change in water production from baseline to latest month in latest report
    #production_new = results.aggregate(Sum("calculated_production_monthly_gallons_month_2014"))
    #production_new = int(production_new["calculated_production_monthly_gallons_month_2014__sum"])
    #production_old = results.aggregate(Sum("calculated_production_monthly_gallons_month_2013"))
    #production_old = int(production_old["calculated_production_monthly_gallons_month_2013__sum"])
    #production_change = calculate.percentage_change(production_old, production_new, multiply=True)
    #logger.debug(production_change)

    # trying to calculate the savings for the current month
    #test_savings_2014 = current_data.aggregate(Sum("calculated_production_monthly_gallons_month_2014"))
    #logger.debug(test_savings_2014)

    #test_savings_2013 = current_data.aggregate(Sum("calculated_production_monthly_gallons_month_2013"))
    #logger.debug(test_savings_2013)

    #test = calculate.percentage_change(test_savings_2013["calculated_production_monthly_gallons_month_2013__sum"], test_savings_2014["calculated_production_monthly_gallons_month_2014__sum"])
    #print test

    def _latest_month_latest_report(self, queryset):

        # determine the most recent month from the report
        latest_data = queryset.aggregate(Max("reporting_month"))

        # determine the most recent report
        latest_report_date = queryset.aggregate(Max("report_date"))

        # determine the target report
        target_report = datetime.date(latest_data["reporting_month__max"].year, latest_data["reporting_month__max"].month, latest_data["reporting_month__max"].day)

        # get the latest month data from the latest report
        output = queryset.filter(report_date = latest_report_date["report_date__max"]).filter(reporting_month__gte = target_report)

        # return output
        return output

    def _all_months_latest_report(self, queryset):

        # determine the most recent month from the report
        latest_data = queryset.aggregate(Max("reporting_month"))

        # determine the most recent report
        latest_report_date = queryset.aggregate(Max("report_date"))

        # determine the target report
        target_report = datetime.date(latest_data["reporting_month__max"].year, latest_data["reporting_month__max"].month, latest_data["reporting_month__max"].day)

        output = queryset.filter(report_date = latest_report_date["report_date__max"]).order_by("-reporting_month")

        # return output
        return output

    def _get_second_draft_conservation_tier(self, conservation_placement):
        if conservation_placement != None:
            if conservation_placement < 65:
                conservation_standard = .08
                conservation_tier = 2
            elif conservation_placement >= 65 and conservation_placement < 80:
                conservation_standard = .12
                conservation_tier = 3
            elif conservation_placement >= 80 and conservation_placement < 95:
                conservation_standard = .16
                conservation_tier = 4
            elif conservation_placement >= 95 and conservation_placement < 110:
                conservation_standard = .20
                conservation_tier = 5
            elif conservation_placement >= 110 and conservation_placement < 130:
                conservation_standard = .24
                conservation_tier = 6
            elif conservation_placement >= 130 and conservation_placement < 170:
                conservation_standard = .28
                conservation_tier = 7
            elif conservation_placement >= 170 and conservation_placement < 215:
                conservation_standard = .32
                conservation_tier = 8
            elif conservation_placement >= 215:
                conservation_standard = .36
                conservation_tier = 9
        else:
            conservation_placement = None
            conservation_standard = None
            conservation_tier = None
        output = {
            "conservation_standard": conservation_standard,
            "conservation_tier": conservation_tier,
            "conservation_placement": conservation_placement,
        }
        return output

    def _get_conservation_tier(self, queryset):
        # get the conservation_placement_threshold for an individual agency
        conservation_placement = queryset.filter(reporting_month = "2014-09-01").values("calculated_rgpcd_2014")
        if len(conservation_placement) > 0:
            conservation_placement = conservation_placement[0]["calculated_rgpcd_2014"]
            if conservation_placement < 55:
                conservation_standard = .10
                conservation_tier = 1
            elif conservation_placement >= 55 and conservation_placement < 110:
                conservation_standard = .20
                conservation_tier = 2
            elif conservation_placement >= 110 and conservation_placement < 165:
                conservation_standard = .25
                conservation_tier = 3
            elif conservation_placement > 165:
                conservation_standard = .35
                conservation_tier = 4
        else:
            conservation_placement = None
            conservation_standard = None
            conservation_tier = None
        output = {
            "conservation_standard": conservation_standard,
            "conservation_tier": conservation_tier,
            "conservation_placement": conservation_placement
        }
        return output

    def _get_rolling_avg_rgcpd(self, queryset):
        residential_population = []
        residential_gallons_used = []
        average_days_in_month = []
        for result in queryset:
            residential_population.append(result.total_population_served)
            calendar_calc = calendar.monthrange(result.reporting_month.year, result.reporting_month.month)
            days_in_month = calendar_calc[1]
            average_days_in_month.append(days_in_month)
            if result.units.upper() == "G":
                tmp = result.calculated_production_monthly_gallons_month_2014 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            elif result.units.upper() == "MG":
                tmp = result.calculated_production_monthly_gallons_month_2014 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            elif result.units.upper() == "CCF":
                tmp = result.calculated_production_monthly_gallons_month_2014 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            elif result.units.upper() == "AF":
                tmp = result.calculated_production_monthly_gallons_month_2014 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            else:
                tmp = result.calculated_production_monthly_gallons_month_2014 * result.percent_residential_use
                residential_gallons_used.append(tmp)
        res_gallons = int(sum(residential_gallons_used))
        total_pop = int(sum(residential_population))
        days_avg = sum(average_days_in_month) / len(average_days_in_month)
        output = (res_gallons / total_pop) / days_avg
        return output

    def _get_avg_rgcpd(self, queryset):
        residential_population = []
        residential_gallons_used = []
        days_in_month = calendar.monthrange(queryset[0].reporting_month.year, queryset[0].reporting_month.month)
        for result in queryset:
            residential_population.append(result.total_population_served)
            if result.units.upper() == "G":
                tmp = result.calculated_production_monthly_gallons_month_2014 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            elif result.units.upper() == "MG":
                tmp = result.calculated_production_monthly_gallons_month_2014 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            elif result.units.upper() == "CCF":
                tmp = result.calculated_production_monthly_gallons_month_2014 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            elif result.units.upper() == "AF":
                tmp = result.calculated_production_monthly_gallons_month_2014 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            else:
                tmp = result.calculated_production_monthly_gallons_month_2014 * result.percent_residential_use
                residential_gallons_used.append(tmp)
        res_gallons = int(sum(residential_gallons_used))
        total_pop = int(sum(residential_population))
        output = (res_gallons / total_pop) / days_in_month[1]
        return output

    def _get_last_year_avg_rgcpd(self, queryset):
        residential_population = []
        residential_gallons_used = []
        days_in_month = calendar.monthrange(queryset[0].reporting_month.year, queryset[0].reporting_month.month)
        for result in queryset:
            residential_population.append(result.total_population_served)
            if result.units.upper() == "G":
                tmp = result.calculated_production_monthly_gallons_month_2013 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            elif result.units.upper() == "MG":
                tmp = result.calculated_production_monthly_gallons_month_2013 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            elif result.units.upper() == "CCF":
                tmp = result.calculated_production_monthly_gallons_month_2013 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            elif result.units.upper() == "AF":
                tmp = result.calculated_production_monthly_gallons_month_2013 * result.percent_residential_use
                residential_gallons_used.append(tmp)
            else:
                tmp = result.calculated_production_monthly_gallons_month_2013 * result.percent_residential_use
                residential_gallons_used.append(tmp)
        res_gallons = int(sum(residential_gallons_used))
        total_pop = int(sum(residential_population))
        output = (res_gallons / total_pop) / days_in_month[1]
        return output

    def calculate_values_range(self, min_value, max_value):
        output = max_value - min_value
        return output

    def pct_value_inside_arbitrary_range(self, starting_value, min_value, max_value):
        """
        how to calculate percentage of value inside arbitrary range
        http://math.stackexchange.com/questions/51509/how-to-calculate-percentage-of-value-inside-arbitrary-range
        """
        range_values = max_value - min_value
        distribution_precent = (starting_value - min_value) / range_values
        distribution_precent = distribution_precent * 100
        output = round(distribution_precent, 2)
        return output
