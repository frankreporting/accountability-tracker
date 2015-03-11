# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cali_water', '0010_remove_waterrestriction_restriction'),
    ]

    operations = [
        migrations.AddField(
            model_name='waterrestriction',
            name='restriction',
            field=models.BooleanField(default=False, verbose_name=b'Restrictions In Place'),
            preserve_default=True,
        ),
    ]
