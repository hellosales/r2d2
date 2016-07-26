# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squareup_api', '0016_remove_squareupaccount_in_authorization'),
    ]

    operations = [
        migrations.CreateModel(
            name='SquareupErrorLog',
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
            model_name='squareupaccount',
            name='last_error',
        ),
        migrations.AddField(
            model_name='squareuperrorlog',
            name='account',
            field=models.ForeignKey(to='squareup_api.SquareupAccount'),
        ),
    ]
