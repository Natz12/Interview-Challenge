# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-20 13:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0008_auto_20160320_2108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicprice',
            name='adjusted_close',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='historicprice',
            name='close',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='historicprice',
            name='high',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='historicprice',
            name='low',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='historicprice',
            name='open',
            field=models.FloatField(),
        ),
    ]