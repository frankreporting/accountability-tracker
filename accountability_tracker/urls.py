from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.contrib import admin
import os
import logging

logger = logging.getLogger("accountability_tracker")

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),

    url(r"^admin/", include(admin.site.urls)),

    # url pattern to kick root to index of cali_water application
    url(r"", include("cali_water.urls")),

    # url pattern to kick root to index of maplight_finance application
    url(r"", include("maplight_finance.urls")),

    # batch edit in admin
    url(r"^admin/", include("massadmin.urls")),
]

if settings.DEBUG and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)