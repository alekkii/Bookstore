# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-28 14:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_auto_20180328_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='last_name',
            field=models.CharField(default=0.0, max_length=100),
            preserve_default=False,
        ),
    ]
