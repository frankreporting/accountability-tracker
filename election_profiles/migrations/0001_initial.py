# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import election_profiles.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('candidate', models.CharField(max_length=255)),
                ('contest', models.CharField(max_length=255)),
                ('biofacts', election_profiles.models.SeparatedValuesField()),
                ('priorities', election_profiles.models.SeparatedValuesField()),
                ('questions_url', models.URLField(max_length=1024, null=True, verbose_name=b'Link to candidate Q&A', blank=True)),
                ('candidate_url', models.URLField(max_length=1024, null=True, verbose_name=b'Link to candidate', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
