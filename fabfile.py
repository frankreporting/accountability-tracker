from __future__ import with_statement
from fabric.api import task, env, run, local, roles, cd, execute, hide, puts, sudo, prefix
import os
import sys
import time
import datetime
import logging
import MySQLdb
import random
import yaml
from fabric.operations import prompt
from fabric.contrib.console import confirm
from fabric.context_managers import lcd
from fabric.colors import green
from fabric.contrib import django

django.settings_module("accountability_tracker.settings_production")
from django.conf import settings

#django.project("accountability_tracker")
#import accountability_tracker
#sys.path.append(accountability_tracker.__path__[0])

env.project_name = "accountability_tracker"
env.local_branch = "master"
env.remote_ref = "origin/master"
env.requirements_file = "requirements.txt"
env.use_ssh_config = False

CONFIG_FILE = os.environ.setdefault("ACCOUNTABILITY_TRACKER_CONFIG_PATH", "./development.yml")
CONFIG = yaml.load(open(CONFIG_FILE))

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

"""
development functions
"""

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

"""
bootstrapping functions
"""

def requirements():
    """
    shortcut to install requirements from repository's requirements.txt
    """
    local("pip install -r requirements.txt")

def create_db():
    connection = None
    db_config = CONFIG["database"]
    #create_statement = "CREATE DATABASE %s" % (db_config["database"])
    create_statement = "CREATE DATABASE %s" % ("test_keller")
    try:
        connection = MySQLdb.connect(
            host = db_config["host"],
            user = db_config["username"],
            passwd = db_config["password"]
        )
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(create_statement)
        connection.commit()
    except MySQLdb.DatabaseError, e:
        print "Error %s" % (e)
        sys.exit(1)
    finally:
        if connection:
            connection.close()

def makesecret(length=50, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'):
    """
    generates secret key for use in django settings
    https://github.com/datadesk/django-project-template/blob/master/fabfile/makesecret.py
    """
    key = ''.join(random.choice(allowed_chars) for i in range(length))
    print 'SECRET_KEY = "%s"' % key

def bootstrap():
    with prefix("WORKON_HOME=$HOME/.virtualenvs"):
        with prefix("source /usr/local/bin/virtualenvwrapper.sh"):
            local("mkvirtualenv %s" % (env.project_name))
            with prefix("workon %s" % (env.project_name)):
                requirements()
                time.sleep(2)
                create_db()
                time.sleep(2)
                migrate()
                time.sleep(2)
                local("python manage.py createsuperuser")
                run()

"""
maplight finance deploy functions
"""

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