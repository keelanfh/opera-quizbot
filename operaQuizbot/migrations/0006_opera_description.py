# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-11 12:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operaQuizbot', '0005_opera_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='opera',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
