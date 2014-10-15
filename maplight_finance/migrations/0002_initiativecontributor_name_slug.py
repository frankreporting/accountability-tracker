# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maplight_finance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='initiativecontributor',
            name='name_slug',
            field=models.CharField(max_length=500, null=True, verbose_name=b"Contributor's Name", blank=True),
            preserve_default=True,
        ),
    ]
