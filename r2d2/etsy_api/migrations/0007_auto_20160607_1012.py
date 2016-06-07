# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etsy_api', '0006_etsyaccount_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etsyaccount',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
