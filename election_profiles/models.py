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
    candidate = models.CharField(max_length=255)
    candidate_slug = models.SlugField("Candidate Slug", unique=True, max_length=255, null=True, blank=True)
    contest = models.CharField(max_length=255)
    biofacts = SeparatedValuesField(null=True, blank=True)
    priorities = SeparatedValuesField(null=True, blank=True)
    questions_url = models.URLField("Link to candidate Q&A", max_length=1024, null=True, blank=True)
    candidate_url = models.URLField("Link to candidate", max_length=1024, null=True, blank=True)

    def __unicode__(self):
        return self.candidate

    def save(self, *args, **kwargs):
        super(Candidate, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("detail", [self.candidate_slug])