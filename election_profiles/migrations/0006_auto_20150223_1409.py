# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('election_profiles', '0005_auto_20150219_0449'),
    ]

    operations = [
        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('measure_number', models.CharField(max_length=50)),
                ('measure_name', models.CharField(max_length=255)),
                ('measure_slug', models.SlugField(null=True, max_length=255, blank=True, unique=True, verbose_name=b'Measure Slug')),
                ('city', models.CharField(max_length=255)),
                ('measure_type', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=1024)),
                ('measure_url', models.URLField(max_length=1024, null=True, verbose_name=b'Link to SmartVoter analysis', blank=True)),
                ('create_date', models.DateTimeField(default=datetime.datetime(2015, 2, 23, 22, 9, 51, 668230, tzinfo=utc), auto_now_add=True)),
                ('change_date', models.DateTimeField(default=datetime.datetime(2015, 2, 23, 22, 9, 51, 668230, tzinfo=utc), auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='candidate',
            name='city',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='candidate',
            name='change_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 23, 22, 9, 51, 667072, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='candidate',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 23, 22, 9, 51, 667072, tzinfo=utc), auto_now_add=True),
            preserve_default=True,
        ),
    ]
