# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0017_hydrologicregion'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersupplier',
            name='april_18_reduction',
            field=models.FloatField(null=True, verbose_name=b'April 18 Reduction Percent', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='april_18_rgpcd',
            field=models.FloatField(null=True, verbose_name=b'April 18 RGPCD', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='april_18_tier',
            field=models.IntegerField(null=True, verbose_name=b'April 18 Reduction Tier', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='april_28_reduction',
            field=models.FloatField(null=True, verbose_name=b'April 28 Reduction Percent', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='april_28_rgpcd',
            field=models.FloatField(null=True, verbose_name=b'April 28 RGPCD', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='april_28_tier',
            field=models.IntegerField(null=True, verbose_name=b'April 28 Reduction Tier', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='april_7_reduction',
            field=models.FloatField(null=True, verbose_name=b'April 7 Reduction Percent', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='april_7_rgpcd',
            field=models.FloatField(null=True, verbose_name=b'April 7 RGPCD', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='april_7_tier',
            field=models.IntegerField(null=True, verbose_name=b'April 7 Reduction Tier', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watersuppliermonthlyreport',
            name='hydrologic_region_slug',
            field=models.SlugField(max_length=255, null=True, verbose_name=b'Hydrologic Region Slug', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watersuppliermonthlyreport',
            name='supplier_slug',
            field=models.SlugField(null=True, max_length=255, blank=True, unique=True, verbose_name=b'Water Supplier Slug'),
            preserve_default=True,
        ),
    ]
