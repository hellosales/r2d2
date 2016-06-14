# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etsy_api', '0011_auto_20160613_1024'),
    ]

    operations = [
        migrations.CreateModel(
            name='EtsyRequestToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_token', models.CharField(max_length=255, null=True, blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='etsyaccount',
            name='request_token',
        ),
    ]
