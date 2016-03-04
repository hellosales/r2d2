# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squareup_api', '0002_auto_20160304_0531'),
    ]

    operations = [
        migrations.AddField(
            model_name='squareupaccount',
            name='in_authrization',
            field=models.BooleanField(default=True),
        ),
    ]
