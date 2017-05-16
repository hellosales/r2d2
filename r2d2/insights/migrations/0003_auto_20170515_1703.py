# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0002_insights_insight_history_summary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insight',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
