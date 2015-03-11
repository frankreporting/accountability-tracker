# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0006_watersuppliermonthlyreport_hydrologic_region'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watersuppliermonthlyreport',
            name='hydrologic_region',
        ),
    ]
