# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, db_index=True)),
                ('slug', models.SlugField(unique=True, max_length=255, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateField(auto_now_add=True)),
                ('content', models.TextField()),
                ('subject', models.TextField()),
                ('title', models.CharField(max_length=255, blank=True)),
                ('url', models.URLField(max_length=255, null=True, blank=True)),
                ('is_sent', models.BooleanField(default=False, help_text=b'Uncheck and save to resend')),
                ('is_read', models.BooleanField(default=False)),
                ('category', models.ForeignKey(related_name='notifications', to='notifications.Category')),
                ('user', models.ForeignKey(related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.AlterIndexTogether(
            name='notification',
            index_together=set([('user', 'is_sent', 'is_read')]),
        ),
    ]
