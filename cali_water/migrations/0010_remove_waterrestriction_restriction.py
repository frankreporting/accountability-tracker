# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0009_waterincentive_waterrestriction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='waterrestriction',
            name='restriction',
        ),
    ]
