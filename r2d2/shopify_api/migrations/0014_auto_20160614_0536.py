# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0013_fill_store_urls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifystore',
            name='store_url',
            field=models.URLField(default=b'http://fake.url.com'),
        ),
    ]
