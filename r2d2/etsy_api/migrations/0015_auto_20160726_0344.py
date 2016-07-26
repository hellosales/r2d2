# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etsy_api', '0014_auto_20160614_1156'),
    ]

    operations = [
        migrations.CreateModel(
            name='EtsyErrorLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('error', models.TextField()),
                ('error_description', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='etsyaccount',
            name='last_error',
        ),
        migrations.AddField(
            model_name='etsyerrorlog',
            name='account',
            field=models.ForeignKey(to='etsy_api.EtsyAccount'),
        ),
    ]
