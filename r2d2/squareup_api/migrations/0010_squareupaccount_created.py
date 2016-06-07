# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('squareup_api', '0009_squareupaccount_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='squareupaccount',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
