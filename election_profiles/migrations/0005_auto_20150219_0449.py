# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('election_profiles', '0004_candidate_kpcc_qa_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='change_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 19, 12, 49, 16, 164004, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='candidate',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 19, 12, 49, 16, 164004, tzinfo=utc), auto_now_add=True),
            preserve_default=True,
        ),
    ]
