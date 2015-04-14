# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import accountability_tracker.custom_fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('candidate', models.CharField(max_length=255)),
                ('candidate_slug', models.SlugField(null=True, max_length=255, blank=True, unique=True, verbose_name=b'Candidate Slug')),
                ('contest', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255, null=True, blank=True)),
                ('biofacts', accountability_tracker.custom_fields.SeparatedValuesField(null=True, blank=True)),
                ('priorities', accountability_tracker.custom_fields.SeparatedValuesField(null=True, blank=True)),
                ('questions_url', models.URLField(max_length=1024, null=True, verbose_name=b'Link to candidate Q&A', blank=True)),
                ('candidate_url', models.URLField(max_length=1024, null=True, verbose_name=b'Link to candidate', blank=True)),
                ('kpcc_qa_url', models.URLField(max_length=1024, null=True, verbose_name=b'Link to KPCC Q&A', blank=True)),
                ('create_date', models.DateTimeField(default=datetime.datetime(2015, 4, 14, 1, 16, 29, 776506, tzinfo=utc), auto_now_add=True)),
                ('change_date', models.DateTimeField(default=datetime.datetime(2015, 4, 14, 1, 16, 29, 776506, tzinfo=utc), auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contest_name', models.CharField(max_length=255)),
                ('contest_slug', models.SlugField(null=True, max_length=255, blank=True, unique=True, verbose_name=b'Contest Slug')),
                ('city', models.CharField(max_length=255)),
                ('contest_url', models.URLField(max_length=1024, null=True, verbose_name=b'Link to SmartVoter contest page', blank=True)),
                ('create_date', models.DateTimeField(default=datetime.datetime(2015, 4, 14, 1, 16, 29, 778048, tzinfo=utc), auto_now_add=True)),
                ('change_date', models.DateTimeField(default=datetime.datetime(2015, 4, 14, 1, 16, 29, 778048, tzinfo=utc), auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('measure_number', models.CharField(max_length=50)),
                ('measure_name', models.CharField(max_length=255)),
                ('measure_slug', models.SlugField(null=True, max_length=255, blank=True, unique=True, verbose_name=b'Measure Slug')),
                ('city', models.CharField(max_length=255)),
                ('measure_type', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=1024)),
                ('measure_url', models.URLField(max_length=1024, null=True, verbose_name=b'Link to SmartVoter analysis', blank=True)),
                ('create_date', models.DateTimeField(default=datetime.datetime(2015, 4, 14, 1, 16, 29, 777326, tzinfo=utc), auto_now_add=True)),
                ('change_date', models.DateTimeField(default=datetime.datetime(2015, 4, 14, 1, 16, 29, 777326, tzinfo=utc), auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
