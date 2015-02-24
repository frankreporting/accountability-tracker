# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('election_profiles', '0006_auto_20150223_1409'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contest_name', models.CharField(max_length=255)),
                ('contest_slug', models.SlugField(null=True, max_length=255, blank=True, unique=True, verbose_name=b'Contest Slug')),
                ('city', models.CharField(max_length=255)),
                ('contest_url', models.URLField(max_length=1024, null=True, verbose_name=b'Link to SmartVoter contest page', blank=True)),
                ('create_date', models.DateTimeField(default=datetime.datetime(2015, 2, 24, 18, 42, 57, 677924, tzinfo=utc), auto_now_add=True)),
                ('change_date', models.DateTimeField(default=datetime.datetime(2015, 2, 24, 18, 42, 57, 677924, tzinfo=utc), auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='change_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 24, 18, 42, 57, 676314, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='candidate',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 24, 18, 42, 57, 676314, tzinfo=utc), auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measure',
            name='change_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 24, 18, 42, 57, 677213, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='measure',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 24, 18, 42, 57, 677213, tzinfo=utc), auto_now_add=True),
            preserve_default=True,
        ),
    ]
