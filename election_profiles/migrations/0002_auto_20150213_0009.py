# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import accountability_tracker.custom_fields


class Migration(migrations.Migration):

    dependencies = [
        ('election_profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='biofacts',
            field=accountability_tracker.custom_fields.SeparatedValuesField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='candidate',
            name='priorities',
            field=accountability_tracker.custom_fields.SeparatedValuesField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
