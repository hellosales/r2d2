# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0002_insights_insight_history_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='name',
            field=models.CharField(default='Old Channel Name', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='insight',
            name='is_initial',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='insight',
            name='time_period',
            field=models.CharField(default=datetime.datetime(2017, 1, 17, 18, 3, 39, 64515, tzinfo=utc), max_length=100, editable=False),
            preserve_default=False,
        ),
    ]
