# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squareup_api', '0017_auto_20160726_0344'),
    ]

    operations = [
        migrations.AddField(
            model_name='squareupaccount',
            name='update_timeframe',
            field=models.IntegerField(default=180),
        ),
    ]
