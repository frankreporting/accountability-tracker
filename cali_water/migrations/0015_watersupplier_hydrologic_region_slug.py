# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0014_watersuppliermonthlyreport_hydrologic_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersupplier',
            name='hydrologic_region_slug',
            field=models.SlugField(null=True, max_length=255, blank=True, unique=True, verbose_name=b'Hydrologic Region Slug'),
            preserve_default=True,
        ),
    ]
