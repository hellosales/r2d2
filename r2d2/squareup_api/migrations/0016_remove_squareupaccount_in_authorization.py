# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squareup_api', '0015_auto_20160613_1024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='squareupaccount',
            name='in_authorization',
        ),
    ]
