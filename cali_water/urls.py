import os
import logging
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView
from cali_water.views import InitialIndex, ComparisonIndex, EnforcementIndex, RegionDetailView, RegionEmbedView, RegionReportView, SupplierDetailView

urlpatterns = patterns("cali_water.views",

    url(
        regex = r"^$/?",
        view = InitialIndex.as_view(),
        kwargs = {},
        name = "water-usage-index",
    ),

    url(
        regex = r"region/(?P<slug>[-\w]+)/?$",
        view = RegionDetailView.as_view(),
        kwargs = {},
        name = "water-region-display",
    ),

    url(
        regex = r"region/(?P<slug>[-\w]+)/reduction-comparison/?$",
        view = ComparisonIndex.as_view(),
        kwargs = {},
        name = "water-reduction-index",
    ),

    url(
        regex = r"region/(?P<slug>[-\w]+)/enforcement-comparison/?$",
        view = EnforcementIndex.as_view(),
        kwargs = {},
        name = "water-enforcement-index",
    ),

    url(
        regex = r"region/(?P<slug>[-\w]+)/report/?$",
        view = RegionReportView.as_view(),
        kwargs = {},
        name = "water-region-report",
    ),

    url(
        regex = r"share/(?P<slug>[-\w]+)/?$",
        view = RegionEmbedView.as_view(),
        kwargs = {},
        name = "water-region-embed",
    ),

    url(
        regex = r"(?P<slug>[-\w]+)/?$",
        view = SupplierDetailView.as_view(),
        kwargs = {},
        name = "water-supplier-detail",
    ),

)
