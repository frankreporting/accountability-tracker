# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WaterSupplier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('supplier_name', models.CharField(unique=True, max_length=255, verbose_name=b'Water Supplier Name', db_index=True)),
                ('supplier_slug', models.SlugField(max_length=255, null=True, verbose_name=b'Water Supplier Slug', blank=True)),
                ('supplier_url', models.URLField(max_length=1024, null=True, verbose_name=b'URL to analysis', blank=True)),
                ('supplier_mwd_member', models.BooleanField(default=False, verbose_name=b'Member of MWD?')),
                ('created_date', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Date Created')),
                ('supplier_notes', models.TextField(null=True, verbose_name=b'Notes About This Water Supplier', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WaterSupplierMonthlyReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stage_invoked', models.CharField(max_length=255, null=True, verbose_name=b'Stage Invoked', blank=True)),
                ('mandatory_restrictions', models.BooleanField(default=False, verbose_name=b'Mandatory Restrictions')),
                ('reporting_month', models.DateField(default=datetime.date(2015, 1, 1), verbose_name=b'Reporting Month', blank=True)),
                ('total_monthly_potable_water_production_2014', models.FloatField(null=True, verbose_name=b'Total Monthly Potable Water Production 2014', blank=True)),
                ('total_monthly_potable_water_production_2013', models.FloatField(null=True, verbose_name=b'Total Monthly Potable Water Production 2013', blank=True)),
                ('units', models.CharField(max_length=255, null=True, verbose_name=b'Units', blank=True)),
                ('qualification', models.TextField(null=True, verbose_name=b'Qualification', blank=True)),
                ('total_population_served', models.IntegerField(null=True, verbose_name=b'Total Population Served', blank=True)),
                ('reported_rgpcd', models.FloatField(null=True, verbose_name=b'Reported Residential Gallons-per-capita-per-day (starting In September 2014)', blank=True)),
                ('enforcement_actions', models.TextField(null=True, verbose_name=b'Enforcement Actions (Optional)', blank=True)),
                ('implementation', models.TextField(null=True, verbose_name=b'Implementation (Optional)', blank=True)),
                ('recycled_water', models.TextField(null=True, verbose_name=b'Recycled Water (Optional)', blank=True)),
                ('recycled_water_units', models.TextField(null=True, verbose_name=b'Recycled Water Units', blank=True)),
                ('calculated_production_monthly_gallons_month_2014', models.IntegerField(null=True, verbose_name=b'Calculated Production Monthly Gallons Month 2014', blank=True)),
                ('calculated_production_monthly_gallons_month_2013', models.IntegerField(null=True, verbose_name=b'Calculated Production Monthly Gallons Month 2013', blank=True)),
                ('calculated_rgpcd_2014', models.FloatField(db_index=True, null=True, verbose_name=b'CALCULATED RGPCD 2014 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)', blank=True)),
                ('calculated_rgpcd_2013', models.FloatField(db_index=True, null=True, verbose_name=b'CALCULATED RGPCD 2013 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)', blank=True)),
                ('percent_residential_use', models.FloatField(null=True, verbose_name=b'Percent Residential Use', blank=True)),
                ('comments_or_corrections', models.TextField(null=True, verbose_name=b'Comments or Corrections', blank=True)),
                ('hydrologic_region', models.CharField(max_length=255, null=True, verbose_name=b'Hydrologic Region', blank=True)),
                ('supplier_name', models.ForeignKey(to='cali_water.WaterSupplier', to_field=b'supplier_name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
