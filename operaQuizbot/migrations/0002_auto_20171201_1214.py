# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-01 12:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operaQuizbot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='approach_culture',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operaQuizbot.ApproachCultureCategory'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='financial',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operaQuizbot.FinancialCategory'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='opera_goer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operaQuizbot.OperaGoerCategory'),
        ),
    ]
