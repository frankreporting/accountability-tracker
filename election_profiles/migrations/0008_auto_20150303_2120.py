# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('election_profiles', '0007_auto_20150224_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='change_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 4, 5, 20, 19, 815716, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='candidate',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 4, 5, 20, 19, 815716, tzinfo=utc), auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contest',
            name='change_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 4, 5, 20, 19, 817202, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contest',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 4, 5, 20, 19, 817202, tzinfo=utc), auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measure',
            name='change_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 4, 5, 20, 19, 816513, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measure',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 4, 5, 20, 19, 816513, tzinfo=utc), auto_now_add=True),
            preserve_default=True,
        ),
    ]
