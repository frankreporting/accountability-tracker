# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0008_waterconservationmethod'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaterIncentive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('incentives_details', models.TextField(null=True, verbose_name=b'Incentives Details', blank=True)),
                ('incentives_last_updated', models.DateTimeField(verbose_name=b'Incentive Last Updated', blank=True)),
                ('incentives_offered', models.BooleanField(default=False, verbose_name=b'Incentives Offered')),
                ('incentives_url', models.URLField(max_length=1024, null=True, verbose_name=b'URL Turf Incentive Details', blank=True)),
                ('turf_rebate_amount', models.FloatField(null=True, verbose_name=b'Turf Removal Reimbursement Amount', blank=True)),
                ('turf_removal_details', models.TextField(null=True, verbose_name=b'Turf Removal Details', blank=True)),
                ('turf_removal_last_updated', models.DateTimeField(verbose_name=b'Turf Removal Last Updated', blank=True)),
                ('turf_removal_offered', models.BooleanField(default=False, verbose_name=b'Turf Removal Offered')),
                ('turf_removal_url', models.URLField(max_length=1024, null=True, verbose_name=b'URL Turf Removal Details', blank=True)),
                ('supplier_name', models.ForeignKey(to='cali_water.WaterSupplier', to_field=b'supplier_name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WaterRestriction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('restriction_current_status', models.CharField(max_length=255, null=True, verbose_name=b'Current Status', blank=True)),
                ('restriction_current_url', models.URLField(max_length=1024, null=True, verbose_name=b'URL Water Restriction Details', blank=True)),
                ('restriction_violation_fine', models.FloatField(null=True, verbose_name=b'Fine amount for violation of restriction', blank=True)),
                ('restriction_how_enforce', models.TextField(null=True, verbose_name=b'Turf Removal Details', blank=True)),
                ('restriction', models.BooleanField(default=False, verbose_name=b'Restrictions In Place')),
                ('restriction_details', models.TextField(null=True, verbose_name=b'Restriction Details', blank=True)),
                ('restrictions_last_updated', models.DateTimeField(verbose_name=b'Restrictions Last Updated', blank=True)),
                ('supplier_name', models.ForeignKey(to='cali_water.WaterSupplier', to_field=b'supplier_name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
