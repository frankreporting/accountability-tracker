from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from accountability_tracker.custom_fields import SeparatedValuesField
import logging

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

class Candidate(models.Model):
    now = timezone.now()
    candidate = models.CharField(max_length=255)
    candidate_slug = models.SlugField("Candidate Slug", unique=True, max_length=255, null=True, blank=True)
    contest = models.CharField(max_length=255)
    city = models.CharField(max_length=255,blank=True,null=True)
    biofacts = SeparatedValuesField(null=True, blank=True)
    priorities = SeparatedValuesField(null=True, blank=True)
    questions_url = models.URLField("Link to candidate Q&A", max_length=1024, null=True, blank=True)
    candidate_url = models.URLField("Link to candidate", max_length=1024, null=True, blank=True)
    kpcc_qa_url = models.URLField("Link to KPCC Q&A", max_length=1024, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True,default=now)
    change_date = models.DateTimeField(auto_now=True,default=now)

    def __unicode__(self):
        return self.candidate

    def save(self, *args, **kwargs):
        super(Candidate, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("detail", [self.candidate_slug])

class Measure(models.Model):
    now = timezone.now()
    measure_number = models.CharField(max_length=50)
    measure_name = models.CharField(max_length=255)
    measure_slug = models.SlugField("Measure Slug", unique=True, max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    measure_type = models.CharField(max_length=255)
    description = models.CharField(max_length=1024)
    measure_url = models.URLField("Link to SmartVoter analysis", max_length=1024, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True,default=now)
    change_date = models.DateTimeField(auto_now=True,default=now)

    def __unicode__(self):
        return self.measure_number

    def save(self, *args, **kwargs):
        super(Measure, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("detail", [self.measure_slug])

class Contest(models.Model):
    now = timezone.now()
    contest_name = models.CharField(max_length=255)
    contest_slug = models.SlugField("Contest Slug", unique=True, max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    contest_url = models.URLField("Link to SmartVoter contest page", max_length=1024, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True,default=now)
    change_date = models.DateTimeField(auto_now=True,default=now)

    def __unicode__(self):
        return self.contest_name + self.city

    def save(self, *args, **kwargs):
        super(Contest, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("detail", [self.contest_slug])