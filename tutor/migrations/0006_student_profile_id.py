# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-24 17:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0005_delete_bloop'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='profile_id',
            field=models.IntegerField(help_text='ProfileID for google people API', null=True),
        ),
    ]
