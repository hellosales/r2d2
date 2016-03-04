# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squareup_api', '0003_squareupaccount_in_authrization'),
    ]

    operations = [
        migrations.RenameField(
            model_name='squareupaccount',
            old_name='in_authrization',
            new_name='in_authorization',
        ),
    ]
