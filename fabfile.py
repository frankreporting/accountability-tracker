from __future__ import with_statement
import os
import time
import datetime
import logging
from fabric.operations import prompt
from fabric.api import local, cd, run, env
from fabric.contrib.console import confirm
from fabric.context_managers import lcd
from fabric.colors import green
from fabric.contrib import django
django.settings_module("accountability_tracker.settings_development")
from django.conf import settings

env.use_ssh_config = True

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

# development functions
def run():
    local("python manage.py runserver")

def make():
    local("python manage.py makemigrations")

def migrate():
    # production function to manually run the scraper in local environment
    local("python manage.py migrate")

def requirements():
    local("pip install -r requirements.txt")

def data():
    local("python manage.py ingest_contributor_data")

def build():
    local("python manage.py build")

def buildserver():
    local("python manage.py buildserver")

def move():
    local("python manage.py move_baked_files")

def commit(message='updates'):
    with lcd(settings.DEPLOY_DIR):
        try:
            message = raw_input("Enter a git commit message:  ")
            local("git add -A && git commit -m \"%s\"" % message)
        except:
            print(green("Nothing new to commit.", bold=False))
        local("git push")

def deploy():
    data()
    time.sleep(5)
    build()
    time.sleep(5)
    local("python manage.py move_baked_files")
    time.sleep(5)
    commit()

def __env_cmd(cmd):
    return env.bin_root + cmd