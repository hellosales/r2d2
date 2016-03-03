# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopifyStore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(max_length=255)),
                ('access_token', models.CharField(max_length=255, null=True, blank=True)),
                ('authorization_date', models.DateTimeField(null=True, blank=True)),
                ('last_successfull_call', models.DateTimeField(null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='shopifystore',
            unique_together=set([('user', 'name')]),
        ),
    ]
