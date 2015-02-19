import os
import logging
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView
from election_profiles.views import InitialListView, InitialDetailView

urlpatterns = patterns("election_profiles.views",

    url(
        regex = r"^$",
        view = InitialListView.as_view(),
        kwargs = {},
        name = "index",
    ),

    url(
        regex = r"(?P<slug>[-\w]+)$",
        view = InitialDetailView.as_view(),
        kwargs = {},
        name = "election-profiles-detail",
    ),

)
