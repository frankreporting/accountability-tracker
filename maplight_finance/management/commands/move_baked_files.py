from django.conf import settings
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

logger = logging.getLogger("accountability_tracker")


def move_my_files(src, dest):
    """  """
    shutil.rmtree(dest)

    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            print('Directory not copied. Error: %s' % e)


class Command(BaseCommand):
    help = "Imports csv to django model"
    def handle(self, *args, **options):
        move_my_files(settings.BUILD_DIR, settings.DEPLOY_DIR)
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))