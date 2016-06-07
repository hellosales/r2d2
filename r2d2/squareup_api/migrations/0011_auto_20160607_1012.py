# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squareup_api', '0010_squareupaccount_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='squareupaccount',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
