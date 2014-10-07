import os
import logging
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView
from maplight_finance.views import index, DummyListView, DummyDetailView

urlpatterns = patterns('maplight_finance.views',

    url(
        regex = r"^initiatives/$",
        view = DummyListView.as_view(),
        kwargs = {},
        name = "index",
    ),

    url(
        regex = r'initiatives/(?P<slug>[-\w]+)/$',
        view = DummyDetailView.as_view(),
        kwargs = {},
        name = "detail",
    ),
)
