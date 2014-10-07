from __future__ import with_statement
from django.conf import settings
import os
import time
import datetime
import logging
from fabric.operations import prompt
from fabric.api import local, cd, run, env
from fabric.contrib.console import confirm
from fabric.context_managers import cd
from fabric.colors import green

env.use_ssh_config = True

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

# development functions

def build_commit(warn_only=True):
    """Build a commit"""
    local_branch = prompt("checkout branch: ")
    rebase_branch = prompt("rebase branch: ")

    local('git checkout %s' % local_branch)
    local('git add .')
    local('git add -u .')

    message  = prompt("commit message: ")

    local('git commit -m "%s"' % message)
    local('git checkout %s' % rebase_branch)
    local('git pull origin %s' % rebase_branch)
    local('git checkout %s' % local_branch)
    local('git rebase %s' % rebase_branch)
    local('git checkout %s' % rebase_branch)
    local('git merge %s' % local_branch)
    local('git push origin %s' % rebase_branch)
    local('git checkout %s' % local_branch)


def run():
    local("python manage.py runserver")

def make():
    local("python manage.py makemigrations")

def migrate():
    # production function to manually run the scraper in local environment
    local("python manage.py migrate")

def data():
    local("python manage.py ingest_contributor_data")

def build():
    local("python manage.py build --skip-static")

def buildserver():
    local("python manage.py buildserver")

def deploy():
    build()
    local("python manage.py move_baked_files")

def __env_cmd(cmd):
    return env.bin_root + cmd