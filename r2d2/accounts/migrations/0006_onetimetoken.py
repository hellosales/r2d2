# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_account_last_fetched_all'),
    ]

    operations = [
        migrations.CreateModel(
            name='OneTimeToken',
            fields=[
                ('key', models.CharField(max_length=40, serialize=False, verbose_name='Key', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('user', models.OneToOneField(related_name='one_time_auth_token', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'One Time Token',
                'verbose_name_plural': 'One Time Tokens',
            },
        ),
    ]
