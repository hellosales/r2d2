# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etsy_api', '0002_auto_20160323_0647'),
    ]

    operations = [
        migrations.AddField(
            model_name='etsyaccount',
            name='fetch_scheduled_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
