# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0007_remove_watersuppliermonthlyreport_hydrologic_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaterConservationMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('method_name', models.CharField(max_length=255, null=True, verbose_name=b'Water Conservation Method Name', blank=True)),
                ('method_slug', models.SlugField(max_length=255, null=True, verbose_name=b'Water Conservation Method Slug', blank=True)),
                ('method_text', models.TextField(null=True, verbose_name=b'Water Conservation Method Text', blank=True)),
                ('method_image_path', models.URLField(max_length=1024, null=True, verbose_name=b'Image Path for Conservation Method', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
