# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0003_auto_20150126_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watersuppliermonthlyreport',
            name='calculated_production_monthly_gallons_month_2013',
            field=models.FloatField(null=True, verbose_name=b'Calculated Production Monthly Gallons Month 2013', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='watersuppliermonthlyreport',
            name='calculated_production_monthly_gallons_month_2014',
            field=models.FloatField(null=True, verbose_name=b'Calculated Production Monthly Gallons Month 2014', blank=True),
            preserve_default=True,
        ),
    ]
