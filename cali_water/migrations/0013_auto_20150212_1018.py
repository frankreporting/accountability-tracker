# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0012_auto_20150203_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watersuppliermonthlyreport',
            name='report_date',
            field=models.DateField(default=datetime.datetime.now, db_index=True, verbose_name=b'Report Date', blank=True),
            preserve_default=True,
        ),
    ]
