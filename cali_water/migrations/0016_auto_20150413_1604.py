# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0015_watersupplier_hydrologic_region_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watersupplier',
            name='hydrologic_region_slug',
            field=models.SlugField(max_length=255, null=True, verbose_name=b'Hydrologic Region Slug', blank=True),
            preserve_default=True,
        ),
    ]
