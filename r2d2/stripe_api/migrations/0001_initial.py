# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import r2d2.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('access_token', models.CharField(max_length=255)),
                ('authorization_date', models.DateTimeField()),
                ('last_successfull_call', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('fetch_status', models.CharField(default=b'idle', max_length=20, db_index=True, choices=[(b'idle', b'Idle'), (b'scheduled', b'Scheduled'), (b'in progress', b'In progress'), (b'failed', b'Failed'), (b'success', b'Success')])),
                ('fetch_scheduled_at', models.DateTimeField(null=True, blank=True)),
                ('last_api_items_dates', r2d2.utils.fields.JSONField(default={}, help_text=b'used for querying API only for updates', blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StripeErrorLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('error', models.TextField()),
                ('error_description', models.TextField(null=True, blank=True)),
                ('account', models.ForeignKey(to='stripe_api.StripeAccount')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='stripeaccount',
            unique_together=set([('user', 'name')]),
        ),
    ]
