# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0002_insightattachment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insightattachment',
            name='insight',
            field=models.ForeignKey(related_name='attachments', to='insights.Insight'),
        ),
    ]
