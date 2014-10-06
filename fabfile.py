from __future__ import with_statement
import os
import time
import datetime
import logging
from fabric.operations import prompt
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.colors import green

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

# development functions
def lrun():
    """
    runs local dev server
    """
    local("python manage.py runserver")

def lmake():
    # production function to manually run the scraper in local environment
    local("python manage.py makemigrations")

def lmigrate():
    # production function to manually run the scraper in local environment
    local("python manage.py migrate")

def __env_cmd(cmd):
    return env.bin_root + cmd