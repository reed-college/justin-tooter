# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-24 21:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0009_auto_20170524_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='profile_id',
            field=models.CharField(help_text='ProfileID for google people API', max_length=50, null=True),
        ),
    ]