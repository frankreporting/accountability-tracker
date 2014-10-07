import os
import logging
from django.conf import settings
from django.conf.urls import patterns, include, url
from maplight_finance.views import index

urlpatterns = patterns('',
    url(
        regex   = r'^$',
        view    = index,
        kwargs  = {},
        name    = 'index',
    ),
)
