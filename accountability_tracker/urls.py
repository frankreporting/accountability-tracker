import os
import logging
import settings_development
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView
from django.contrib import admin

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

# enable the admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    # url pattern to kick root to index of maplight_finance application
    url(r'', include('maplight_finance.urls')),

    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        #'document_root': settings_development.STATIC_ROOT, 'show_indexes': settings_development.DEBUG
    #}),
)