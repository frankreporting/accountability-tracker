from django.conf import settings
import django.core.urlresolvers
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str, smart_unicode
from django.utils.timezone import utc, localtime
from django.core.mail import send_mail, mail_admins, send_mass_mail, EmailMessage
from maplight_finance.models import Initiative, InitiativeContributor
import os
import sys
import time
import shutil
import errno
import logging
from subprocess import Popen, PIPE
import datetime
import posixpath

logger = logging.getLogger("accountability_tracker")

def test():

    settings.ARCHIVE_PATH = ""

    old_static_url = settings.STATIC_URL.replace("/", "")
    projects_subdirectory = settings.DEPLOY_DIR
    what_is_this = "%s/%s" % (projects_subdirectory, old_static_url)
    logger.debug(what_is_this)






class Command(BaseCommand):
    help = "Imports csv to django model"
    def handle(self, *args, **options):
        test()
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
