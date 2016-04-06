# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import r2d2.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0003_shopifystore_fetch_scheduled_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifystore',
            name='last_api_items_dates',
            field=r2d2.utils.fields.JSONField(default={}, help_text=b'used for querying API only for updates', blank=True),
        ),
    ]
