# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0019_auto_20150501_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaterEnforcementMonthlyReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('report_date', models.DateField(default=datetime.datetime.now, db_index=True, verbose_name=b'Report Date', blank=True)),
                ('reported_to_state_date', models.DateField(default=datetime.datetime.now, db_index=True, verbose_name=b'Date Reported to the State', blank=True)),
                ('reporting_month', models.DateField(default=datetime.date(2015, 1, 1), verbose_name=b'Reporting Month', blank=True)),
                ('supplier_id', models.IntegerField(null=True, verbose_name=b'Supplier ID', blank=True)),
                ('supplier_name', models.CharField(max_length=255, verbose_name=b'Water Supplier Name', db_index=True)),
                ('supplier_slug', models.SlugField(max_length=255, null=True, verbose_name=b'Water Supplier Slug', blank=True)),
                ('hydrologic_region', models.CharField(db_index=True, max_length=255, null=True, verbose_name=b'Hydrologic Region', blank=True)),
                ('hydrologic_region_slug', models.SlugField(max_length=255, null=True, verbose_name=b'Hydrologic Region Slug', blank=True)),
                ('total_population_served', models.IntegerField(null=True, verbose_name=b'Total Population Served', blank=True)),
                ('mandatory_restrictions', models.BooleanField(default=False, verbose_name=b'Mandatory Restrictions')),
                ('water_days_allowed_week', models.IntegerField(null=True, verbose_name=b'Water Days Allowed/Week', blank=True)),
                ('complaints_received', models.IntegerField(null=True, verbose_name=b'Complaints Received', blank=True)),
                ('follow_up_actions', models.IntegerField(null=True, verbose_name=b'Follow-up Actions', blank=True)),
                ('warnings_issued', models.IntegerField(null=True, verbose_name=b'Warnings Issued', blank=True)),
                ('penalties_assessed', models.IntegerField(null=True, verbose_name=b'Penalties Assessed', blank=True)),
                ('enforcement_comments', models.TextField(null=True, verbose_name=b'Enforcement Comments', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
