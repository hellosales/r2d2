# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0006_shopifystore_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifystore',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
