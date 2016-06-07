# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('etsy_api', '0005_etsyaccount_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='etsyaccount',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
