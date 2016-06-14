# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('etsy_api', '0012_auto_20160614_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='etsyrequesttoken',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
