# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0018_auto_20150501_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watersuppliermonthlyreport',
            name='hydrologic_region',
            field=models.CharField(db_index=True, max_length=255, null=True, verbose_name=b'Hydrologic Region', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='watersuppliermonthlyreport',
            name='supplier_slug',
            field=models.SlugField(max_length=255, null=True, verbose_name=b'Water Supplier Slug', blank=True),
            preserve_default=True,
        ),
    ]
