# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maplight_finance', '0002_initiativecontributor_name_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='initiativecontributor',
            name='data_as_of_date',
            field=models.DateField(null=True, verbose_name=b'Last Maplight Update', blank=True),
            preserve_default=True,
        ),
    ]
