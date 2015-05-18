# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0013_auto_20150212_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersuppliermonthlyreport',
            name='hydrologic_region',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Hydrologic Region', blank=True),
            preserve_default=True,
        ),
    ]
