# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import r2d2.insights.models


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InsightAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'insights_attachments', validators=[r2d2.insights.models.validate_file_extension])),
                ('insight', models.ForeignKey(to='insights.Insight')),
            ],
        ),
    ]
