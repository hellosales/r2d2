# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_api', '0003_stripeaccount_the_refresh_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripeaccount',
            name='merchant_id',
            field=models.CharField(default=1, max_length=255, blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stripeaccount',
            name='the_refresh_token',
            field=models.CharField(default=None, max_length=255, blank=True),
            preserve_default=False,
        ),
    ]
