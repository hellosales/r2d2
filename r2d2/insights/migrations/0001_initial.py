# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import r2d2.insights.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InsightHistorySummary',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('insight_model_id', models.IntegerField()),
                ('count_insights', models.IntegerField()),
                ('most_recent', models.DateTimeField()),
            ],
            options={
                'db_table': 'insights_insight_history_summary',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('official_channel_name', models.CharField(max_length=500)),
                ('data_importer_class', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Insight',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('generator_class', models.CharField(max_length=100, editable=False)),
                ('insight_model_id', models.IntegerField()),
                ('was_helpful', models.NullBooleanField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InsightAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_type', models.CharField(max_length=50, null=True)),
<<<<<<< Updated upstream
                ('file', models.FileField(upload_to=b'insights_attachments', validators=[r2d2.insights.models.validate_file_extension])),
=======
                ('file', models.FileField(upload_to=b'insights_attachments',
                                          validators=[r2d2.insights.models.validate_file_extension])),
>>>>>>> Stashed changes
                ('insight', models.ForeignKey(related_name='attachments', to='insights.Insight')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sku', models.CharField(max_length=500)),
                ('name', models.CharField(max_length=500)),
                ('insight', models.ForeignKey(to='insights.Insight')),
            ],
        ),
        migrations.AddField(
            model_name='channel',
            name='insight',
            field=models.ForeignKey(to='insights.Insight'),
        ),
    ]
