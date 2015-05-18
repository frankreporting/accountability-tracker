# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0016_auto_20150413_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='HydrologicRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hydrologic_region', models.CharField(max_length=255, null=True, verbose_name=b'Hydrologic Region', blank=True)),
                ('hydrologic_region_slug', models.SlugField(max_length=255, null=True, verbose_name=b'Hydrologic Region Slug', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
