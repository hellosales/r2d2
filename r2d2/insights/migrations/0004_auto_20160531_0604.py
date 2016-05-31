# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0003_auto_20160527_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='insightattachment',
            name='content_type',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='insight',
            name='generator_class',
            field=models.CharField(max_length=100, editable=False),
        ),
    ]
