# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0003_auto_20170117_1303'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='data_importer_class',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='official_channel_name',
        ),
    ]
