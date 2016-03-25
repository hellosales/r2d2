# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import r2d2.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('etsy_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='etsyaccount',
            name='fetch_status',
            field=models.CharField(default=b'idle', max_length=20, db_index=True, choices=[(b'idle', b'Idle'), (b'scheduled', b'Scheduled'), (b'in progress', b'In progress'), (b'failed', b'Failed'), (b'success', b'Success')]),
        ),
        migrations.AddField(
            model_name='etsyaccount',
            name='last_api_items_dates',
            field=r2d2.utils.fields.JSONField(default={}),
        ),
        migrations.AddField(
            model_name='etsyaccount',
            name='last_error',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='etsyaccount',
            name='name',
            field=models.CharField(max_length=255, db_index=True),
        ),
    ]
