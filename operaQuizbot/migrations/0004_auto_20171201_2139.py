# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-01 21:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaQuizbot', '0003_profile_did_you_know'),
    ]

    operations = [
        migrations.AddField(
            model_name='didyouknowquestion',
            name='image_url',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.AddField(
            model_name='didyouknowquestion',
            name='link_url',
            field=models.CharField(default='', max_length=256),
        ),
    ]
