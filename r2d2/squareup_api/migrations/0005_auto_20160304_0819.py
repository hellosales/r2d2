# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squareup_api', '0004_auto_20160304_0642'),
    ]

    operations = [
        migrations.AddField(
            model_name='squareupaccount',
            name='merchant_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='squareupaccount',
            name='token_expiration',
            field=models.DateTimeField(db_index=True, null=True, blank=True),
        ),
    ]
