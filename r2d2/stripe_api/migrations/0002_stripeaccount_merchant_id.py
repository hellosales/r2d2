# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripeaccount',
            name='merchant_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
