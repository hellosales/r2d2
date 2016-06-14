# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0011_auto_20160613_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopifystore',
            name='store_url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
