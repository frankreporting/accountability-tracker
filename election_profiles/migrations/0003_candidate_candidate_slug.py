# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('election_profiles', '0002_auto_20150213_0009'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='candidate_slug',
            field=models.SlugField(null=True, max_length=255, blank=True, unique=True, verbose_name=b'Candidate Slug'),
            preserve_default=True,
        ),
    ]
