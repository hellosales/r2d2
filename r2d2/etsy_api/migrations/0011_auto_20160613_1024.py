# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etsy_api', '0010_drop_unauthorized_accounts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etsyaccount',
            name='access_token',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='etsyaccount',
            name='authorization_date',
            field=models.DateTimeField(),
        ),
    ]
