from django.conf import settings
from django.contrib import admin
from django.db import models as dmodels
from social_pols.models import PoliticianTwitterAccount, PoliticianTweet
from django.utils.timezone import utc, localtime
import time
import datetime
import logging
from datetime import tzinfo
import pytz
from pytz import timezone


logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)


class PoliticianTwitterAccountAdmin(admin.ModelAdmin):
    list_display = ("candidate_name", "race",  "user_screen_name",)
    list_per_page = 10
    search_fields = ["candidate_name", "race",  "user_screen_name",]
    list_filter = ["race"]
    ordering = ("-race",)


class PoliticianTweetAdmin(admin.ModelAdmin):
    list_display = ("user_screen_name", "text")
    list_per_page = 10
    search_fields = ["user_screen_name", "text"]
    list_filter = ["user_screen_name"]
    ordering = ("-user_screen_name",)


admin.site.register(PoliticianTwitterAccount, PoliticianTwitterAccountAdmin)
admin.site.register(PoliticianTweet, PoliticianTweetAdmin)
