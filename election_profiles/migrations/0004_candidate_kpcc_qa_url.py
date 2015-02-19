# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('election_profiles', '0003_candidate_candidate_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='kpcc_qa_url',
            field=models.URLField(max_length=1024, null=True, verbose_name=b'Link to KPCC Q&A', blank=True),
            preserve_default=True,
        ),
    ]
