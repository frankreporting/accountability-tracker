# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0002_auto_20150126_1321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watersupplier',
            name='supplier_slug',
            field=models.SlugField(null=True, max_length=255, blank=True, unique=True, verbose_name=b'Water Supplier Slug'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='watersupplier',
            name='supplier_url',
            field=models.URLField(max_length=1024, null=True, verbose_name=b'URL to Water Supplier Home Page', blank=True),
            preserve_default=True,
        ),
    ]
