# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0004_auto_20170119_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='data_importer_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='channel',
            name='data_importer_name',
            field=models.CharField(default='temp', max_length=200, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='insight',
            name='data_importer_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='insight',
            name='data_importer_name',
            field=models.CharField(default='temp', max_length=200, editable=False),
            preserve_default=False,
        ),
    ]
