# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('squareup_api', '0012_auto_20160607_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='squareupaccount',
            name='access_token',
            field=models.CharField(default=b'fake_token', max_length=255),
        ),
        migrations.AlterField(
            model_name='squareupaccount',
            name='authorization_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
