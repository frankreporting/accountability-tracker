# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Initiative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('initiative_identifier', models.CharField(max_length=500, null=True, verbose_name=b'Initiative', blank=True)),
                ('initiative_slug', models.SlugField(max_length=140, null=True, verbose_name=b'Initiative Slug', blank=True)),
                ('description', models.CharField(max_length=500, null=True, verbose_name=b'Initiative description', blank=True)),
                ('document_url', models.URLField(max_length=1024, null=True, verbose_name=b'URL to analysis', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InitiativeContributor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stance', models.CharField(max_length=500, null=True, verbose_name=b'Stance on Initiative', blank=True)),
                ('transaction_name', models.CharField(max_length=500, null=True, verbose_name=b'Transaction Name', blank=True)),
                ('committee_id', models.CharField(max_length=500, null=True, blank=True)),
                ('name', models.CharField(max_length=500, null=True, verbose_name=b"Contributor's Name", blank=True)),
                ('employer', models.CharField(max_length=500, null=True, verbose_name=b"Contributor's Employer", blank=True)),
                ('occupation', models.CharField(max_length=500, null=True, verbose_name=b"Contributor's Occupation", blank=True)),
                ('city', models.CharField(max_length=500, null=True, verbose_name=b"Contributor's City", blank=True)),
                ('state', models.CharField(max_length=500, null=True, verbose_name=b"Contributor's State", blank=True)),
                ('zip_code', models.CharField(max_length=500, null=True, verbose_name=b"Contributor's Zip code", blank=True)),
                ('id_number', models.IntegerField(max_length=500, null=True, blank=True)),
                ('payment_type', models.CharField(max_length=500, null=True, blank=True)),
                ('amount', models.DecimalField(null=True, verbose_name=b"Contributor's Amount", max_digits=11, decimal_places=2, blank=True)),
                ('transaction_date', models.DateField(null=True, verbose_name=b'Transaction Date', blank=True)),
                ('filed_date', models.DateField(null=True, verbose_name=b'Filing Date', blank=True)),
                ('transaction_number', models.CharField(max_length=500, null=True, blank=True)),
                ('is_individual', models.CharField(max_length=500, null=True, blank=True)),
                ('donor_type', models.CharField(max_length=500, null=True, blank=True)),
                ('industry', models.CharField(max_length=500, null=True, blank=True)),
                ('created_date', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'date created')),
                ('initiative_identifier', models.ForeignKey(related_name=b'initiative_initiative_identifier', blank=True, to='maplight_finance.Initiative', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
