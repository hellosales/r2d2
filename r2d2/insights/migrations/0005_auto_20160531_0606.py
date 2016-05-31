# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0004_auto_20160531_0604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insightattachment',
            name='content_type',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
