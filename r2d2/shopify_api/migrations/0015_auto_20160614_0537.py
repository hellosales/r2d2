# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0014_auto_20160614_0536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifystore',
            name='store_url',
            field=models.URLField(),
        ),
    ]
