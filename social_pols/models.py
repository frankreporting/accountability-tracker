from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
import logging
import time
import datetime

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

class PoliticianTwitterAccount(models.Model):
    race = models.CharField(max_length=500, null=True, blank=True)
    candidate_name = models.CharField(max_length=500, null=True, blank=True)
    user_screen_name = models.CharField(max_length=500, null=True, blank=True)

class PoliticianTweet(models.Model):
    tweet_id = models.CharField(max_length=500, null=True, blank=True)
    text = models.CharField(max_length=500, null=True, blank=True)
    in_reply_to_status_id = models.CharField(max_length=500, null=True, blank=True)
    favorite_count = models.IntegerField(max_length=500, null=True, blank=True)
    user_name = models.CharField(max_length=500, null=True, blank=True)
    user_screen_name = models.CharField(max_length=500, null=True, blank=True)
    source = models.CharField(max_length=500, null=True, blank=True)
    coordinates = models.CharField(max_length=500, null=True, blank=True)
    retweet_count = models.IntegerField(max_length=500, null=True, blank=True)
    user_followers_count = models.IntegerField(max_length=500, null=True, blank=True)
    user_location = models.CharField(max_length=500, null=True, blank=True)
    user_description = models.CharField(max_length=500, null=True, blank=True)
    tweet_url = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField()
    in_reply_to_user_id = models.CharField(max_length=500, null=True, blank=True)
    user_profile_location = models.CharField(max_length=500, null=True, blank=True)
    user_statuses_count = models.IntegerField(max_length=500, null=True, blank=True)
    user_friends_count = models.IntegerField(max_length=500, null=True, blank=True)
    user_created_at = models.DateTimeField()
    user_contributors_enabled = models.CharField(max_length=500, null=True, blank=True)
    geo = models.CharField(max_length=500, null=True, blank=True)
    full_name = models.CharField(max_length=500, null=True, blank=True)
    country = models.CharField(max_length=500, null=True, blank=True)
    place_type = models.CharField(max_length=500, null=True, blank=True)
    bounding_box = models.CharField(max_length=500, null=True, blank=True)
    contained_within = models.CharField(max_length=500, null=True, blank=True)
    country_code = models.CharField(max_length=500, null=True, blank=True)
    place = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.id
