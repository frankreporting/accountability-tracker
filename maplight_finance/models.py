from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
import logging
import time
import datetime

logger = logging.getLogger("root")
logging.basicConfig(
    format = "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)

# Create your models here.

class Initiative(models.Model):
    initiative_identifier = models.CharField("Initiative", max_length=500, null=True, blank=True)
    initiative_slug = models.SlugField("Initiative Slug", max_length=140, null=True, blank=True)
    description = models.CharField("Initiative description", max_length=500, null=True, blank=True)
    document_url = models.URLField("URL to analysis", max_length=1024, null=True, blank=True)

    def __unicode__(self):
        return self.initiative_identifier

    @models.permalink
    def get_absolute_url(self):
        return ("detail", [self.initiative_slug])

class InitiativeContributor(models.Model):
    initiative_identifier = models.ForeignKey(Initiative, null=True, blank=True, related_name="initiative_initiative_identifier")
    stance = models.CharField("Stance on Initiative", max_length=500, null=True, blank=True)
    transaction_name = models.CharField("Transaction Name", max_length=500, null=True, blank=True)
    committee_id = models.CharField(max_length=500, null=True, blank=True)
    name = models.CharField("Contributor's Name", max_length=500, null=True, blank=True)
    name_slug = models.CharField("Contributor's Name", max_length=500, null=True, blank=True)
    employer = models.CharField("Contributor's Employer", max_length=500, null=True, blank=True)
    occupation = models.CharField("Contributor's Occupation", max_length=500, null=True, blank=True)
    city = models.CharField("Contributor's City", max_length=500, null=True, blank=True)
    state = models.CharField("Contributor's State", max_length=500, null=True, blank=True)
    zip_code = models.CharField("Contributor's Zip code", max_length=500, null=True, blank=True)
    id_number = models.IntegerField(max_length=500, null=True, blank=True)
    payment_type = models.CharField(max_length=500, null=True, blank=True)
    amount = models.DecimalField("Contributor's Amount", max_digits=11, decimal_places=2, null=True, blank=True)
    transaction_date = models.DateField("Transaction Date", null=True, blank=True)
    filed_date = models.DateField("Filing Date", null=True, blank=True)
    transaction_number = models.CharField(max_length=500, null=True, blank=True)
    is_individual = models.CharField(max_length=500, null=True, blank=True)
    donor_type = models.CharField(max_length=500, null=True, blank=True)
    industry = models.CharField(max_length=500, null=True, blank=True)
    data_as_of_date = models.DateField("Last Maplight Update", null=True, blank=True)
    created_date = models.DateTimeField("date created", default=datetime.datetime.now)

    def __unicode__(self):
        return self.transaction_number

    #@models.permalink
    #def get_absolute_url(self):
        #return ("what-detail", [self.id,])