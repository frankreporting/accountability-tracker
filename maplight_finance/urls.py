import os
import logging
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView
from maplight_finance.views import index, InitialListView, InitialDetailView

urlpatterns = patterns('maplight_finance.views',

    #url(
        #regex = r"^$",
        #view = InitialListView.as_view(),
        #kwargs = {},
        #name = "index",
    #),

    url(
        regex = r'(?P<slug>[-\w]+)/$',
        view = InitialDetailView.as_view(),
        kwargs = {},
        name = "detail",
    ),
)
