# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0010_drop_unauthorized_accounts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopifystore',
            name='access_token',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='shopifystore',
            name='authorization_date',
            field=models.DateTimeField(),
        ),
    ]
