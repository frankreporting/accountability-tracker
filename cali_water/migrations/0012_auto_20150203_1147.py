# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0011_waterrestriction_restriction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watersuppliermonthlyreport',
            name='report_date',
            field=models.CharField(db_index=True, max_length=255, null=True, verbose_name=b'Report Date', blank=True),
            preserve_default=True,
        ),
    ]
