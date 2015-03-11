# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0004_auto_20150126_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersuppliermonthlyreport',
            name='report_date',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Report Date', blank=True),
            preserve_default=True,
        ),
    ]
