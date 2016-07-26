# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0015_auto_20160614_0537'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopifyErrorLog',
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
            model_name='shopifystore',
            name='last_error',
        ),
        migrations.AddField(
            model_name='shopifyerrorlog',
            name='account',
            field=models.ForeignKey(to='shopify_api.ShopifyStore'),
        ),
    ]
