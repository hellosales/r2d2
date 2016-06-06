# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_adjust_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='last_fetched_all',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
