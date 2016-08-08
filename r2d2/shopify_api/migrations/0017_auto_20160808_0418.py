# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0016_auto_20160726_0344'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shopifystore',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='shopifystore',
            unique_together=set([('user', 'name'), ('user', 'store_url')]),
        ),
    ]
