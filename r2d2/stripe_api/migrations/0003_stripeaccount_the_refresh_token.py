# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_api', '0002_stripeaccount_merchant_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripeaccount',
            name='the_refresh_token',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
