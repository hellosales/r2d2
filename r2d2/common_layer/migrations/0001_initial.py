# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('currency', models.CharField(max_length=3)),
                ('value', models.DecimalField(max_digits=20, decimal_places=6)),
                ('date', models.DateField()),
            ],
            options={
                'db_table': 'djmoney_rates_rate',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ExchangeRateSource',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('last_update', models.DateField()),
                ('base_currency', models.CharField(max_length=3)),
            ],
            options={
                'db_table': 'djmoney_rates_ratesource',
                'managed': False,
            },
        ),
    ]
