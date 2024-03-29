from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
import logging

# Create your models here.
class Initiative(models.Model):
    ag_id = models.CharField(max_length=10,blank=True)
    id_note = models.CharField(max_length=200,blank=True)
    sos_id = models.CharField(max_length=10,blank=True)
    title = models.CharField(max_length=999,blank=True)
    summary = models.CharField(max_length=9999,blank=True)
    proponent = models.CharField(max_length=200,blank=True)
    email = models.CharField(max_length=200,blank=True)
    phone = models.CharField(max_length=20,blank=True)
    date_sum = models.DateTimeField('Summary Date',blank=True,null=True)
    date_sum_estimate = models.DateTimeField('Estimated Date for Title/Summary',blank=True,null=True)
    status = models.CharField(max_length=50,blank=True)
    date_circulation_deadline = models.DateTimeField('Circulation Deadline',blank=True,null=True)
    sigs_req = models.CharField(max_length=10,blank=True,null=True)
    date_qualified = models.DateTimeField('Date Qualified',blank=True,null=True)
    date_failed = models.DateTimeField('Date Failed to Qualify',blank=True,null=True)
    date_sample_due = models.DateTimeField('Date Random Sample Due',blank=True,null=True)
    date_raw_count_due = models.DateTimeField('Date Raw Count Due',blank=True,null=True)
    election = models.CharField(max_length=200,blank=True)
    prop_num = models.CharField(max_length=10,blank=True)
    full_text_link = models.CharField(max_length=200,blank=True)
    date_sample_update = models.DateTimeField('Date Signature Count Updated',blank=True,null=True)
    sig_count_link = models.CharField(max_length=200,blank=True)
    fiscal_impact_link = models.CharField(max_length=200,blank=True)
    proposition_type = models.CharField(max_length=100,blank=True)

    def __unicode__(self):
        return self.title