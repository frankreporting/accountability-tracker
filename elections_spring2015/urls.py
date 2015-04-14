import os
import logging
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView
from elections_spring2015.views import InitialListView, InitialDetailView, MeasureDetailView, ContestListView

urlpatterns = patterns("elections_spring2015.views",

    url(
        regex = r"^/pasadena-april-21/$",
        view = PasadenaListView.as_view(),
        kwargs = {},
        name = "pasadena-index",
    ),

    url(
        regex = r"^/los-angeles-may-19/$",
        view = LosAngelesListView.as_view(),
        kwargs = {},
        name = "losangeles-index",
    ),

    url(
        regex = r"^/pasadena-april-21/(?P<slug>[-\w]+)$",
        view = CandidateDetailView.as_view(),
        kwargs = {},
        name = "spring2015-pasadena-detail",
    ),

    url(
        regex = r"^/los-angeles-may-19/(?P<slug>[-\w]+)$",
        view = CandidateDetailView.as_view(),
        kwargs = {},
        name = "spring2015-los-angeles-detail",
    ),

)
