# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0004_auto_20160406_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopifystore',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
