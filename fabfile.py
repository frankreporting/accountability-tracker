from __future__ import with_statement
from fabric.api import task, env, run, local, roles, cd, execute, hide, puts, sudo, prefix
import os
import time
import datetime
import logging
import MySQLdb
from fabric.operations import prompt
from fabric.contrib.console import confirm
from fabric.context_managers import lcd
from fabric.colors import green
from fabric.contrib import django
django.settings_module("accountability_tracker.settings_production")
from django.conf import settings

env.local_branch = 'master'
env.remote_ref = 'origin/master'
env.requirements_file = 'requirements.txt'
env.use_ssh_config = True

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

def run():
    """
    shortcut for base manage.py function to run the dev server
    """
    local("python manage.py runserver")

def make():
    """
    shortcut for base manage.py function to sync the dev database
    """
    local("python manage.py makemigrations")

def migrate():
    """
    shortcut for base manage.py function to apply db migrations
    """
    local("python manage.py migrate")

def superuser():
    """
    shortcut for base manage.py function to create a superuser
    """
    local("python manage.py createsuperuser")

def requirements():
    """
    shortcut to install requirements from repository's requirements.txt
    """
    local("pip install -r requirements.txt")

#def create_db():
    """
    shortcut to create a development database
    """
    #logger.debug("creating the database")
    #create_connection("CREATE DATABASE %s" % settings.DATABASES["default"]["NAME"])

#def create_connection(target_query):
    #connection = None
    #try:
        #connection = MySQLdb.connect(
            #host = settings.DATABASES["default"]["HOST"],
            #user = settings.DATABASES["default"]["USER"],
            #passwd = settings.DATABASES["default"]["PASSWORD"]
        #)
        #cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute(target_query)
        #connection.commit()
    #except MySQLdb.DatabaseError, e:
        #print "Error %s" % (e)
        #sys.exit(1)
    #finally:
        #if connection:
            #connection.close()

def maplight_test():
    local("python manage.py test maplight_finance")

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