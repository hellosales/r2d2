# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0005_auto_20170123_1336'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channel',
            old_name='data_importer_id',
            new_name='data_provider_id',
        ),
        migrations.RenameField(
            model_name='channel',
            old_name='data_importer_name',
            new_name='data_provider_name',
        ),
        migrations.RenameField(
            model_name='insight',
            old_name='data_importer_id',
            new_name='data_provider_id',
        ),
        migrations.RenameField(
            model_name='insight',
            old_name='data_importer_name',
            new_name='data_provider_name',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='name',
        ),
    ]
