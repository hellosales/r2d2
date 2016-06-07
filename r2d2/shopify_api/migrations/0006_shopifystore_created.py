# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0005_shopifystore_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopifystore',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
