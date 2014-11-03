from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from django.core.mail import send_mail, mail_admins, send_mass_mail, EmailMessage
from django.conf import settings
from social_pols.models import PoliticianTwitterAccount, PoliticianTweet
import os
import csv
import logging
import time
import datetime
import urllib2
import requests
import string
from datetime import tzinfo
from dateutil import parser
import pytz
from pytz import timezone
from twitter import *


logger = logging.getLogger("accountability_tracker")


def search_politician_tweets():
    politician = PoliticianTwitterAccount.objects.exclude(user_screen_name__isnull=True).exclude(user_screen_name__exact='')
    logger.debug(len(politician))
    size_of_loop = len(politician)
    count = 0
    while count < size_of_loop:
        query_screen_name = politician[count].user_screen_name
        logger.debug(query_screen_name)
        results = construct_twitter_search(query_screen_name)
        write_to_database(results)
        count = count + 1
        time.sleep(60)


def construct_twitter_search(user):
    """ reusable function to return tweets """
    twitter_object = Twitter(
        auth=OAuth(
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET,
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET
        )
    )
    tweet_results = twitter_object.statuses.user_timeline(
        screen_name=user
    )
    return tweet_results


def write_to_database(results):
    start_search_time = utc.localize(datetime.datetime(2014, 10, 01, 0, 0))
    for result in results:
        tweet_time = parser.parse(result["created_at"].encode('ascii', 'ignore'))
        if tweet_time > start_search_time:
            try:
                if result["place"] is not None:
                    place = result["place"]
                    full_name = result["place"]["full_name"]
                    country = result["place"]["country"]
                    place_type = result["place"]["place_type"]
                    bounding_box = result["place"]["bounding_box"]
                    contained_within = result["place"]["contained_within"]
                    country_code = result["place"]["country_code"]
                else:
                    place = None
                    full_name = None
                    country = None
                    place_type = None
                    bounding_box = None
                    contained_within = None
                    country_code = None
                obj, created = PoliticianTweet.objects.get_or_create(
                    tweet_id = result["id"],
                    defaults={
                        "text": result["text"].encode('ascii', 'ignore'),
                        "in_reply_to_status_id": result["in_reply_to_status_id"],
                        "favorite_count": result["favorite_count"],
                        "user_name": result["user"]["name"].encode('ascii', 'ignore'),
                        "user_screen_name": result["user"]["screen_name"].encode('ascii', 'ignore'),
                        "source": result["source"].encode('ascii', 'ignore'),
                        "coordinates": result["coordinates"],
                        "retweet_count": result["retweet_count"],
                        "user_followers_count": result["user"]["followers_count"],
                        "user_location": result["user"]["location"].encode('ascii', 'ignore'),
                        "user_description": result["user"]["description"].encode('ascii', 'ignore'),
                        "tweet_url": "https://twitter.com/" + result["user"]["screen_name"].encode('ascii', 'ignore') + "/status/" + str(result["id"]).encode('ascii', 'ignore'),
                        "created_at": parser.parse(result["created_at"].encode('ascii', 'ignore')),
                        "in_reply_to_user_id": result["in_reply_to_user_id"],
                        "user_profile_location": result["user"]["profile_location"],
                        "user_statuses_count": result["user"]["statuses_count"],
                        "user_friends_count": result["user"]["friends_count"],
                        "user_created_at": parser.parse(result["user"]["created_at"]),
                        "user_contributors_enabled": result["user"]["contributors_enabled"],
                        "geo": result["geo"],
                        "full_name": full_name,
                        "country": country,
                        "place_type": place_type,
                        "bounding_box": bounding_box,
                        "contained_within": contained_within,
                        "country_code": country_code,
                        "place": place
                    }
                )
                if not created:
                    logger.debug("Record exists")
                else:
                    logger.debug("New record created for %s" % (result["id"]))
            except Exception, exception:
                logger.error(exception)
                break
        else:
            logger.debug("Tweet is older than %s" % (start_search_time))


class Command(BaseCommand):
    help = "Polls twitter for candidate tweets on election day"
    def handle(self, *args, **options):
        search_politician_tweets()
        self.stdout.write("\nScraping finished at %s\n" % str(datetime.datetime.now()))