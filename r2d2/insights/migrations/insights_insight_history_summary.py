# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import r2d2.insights.models

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insights', '0001_initial'),
    ]

    sql = "DROP VIEW IF EXISTS insights_insight_history_summary; "  # "OR REPLACE"
    sql = sql + "CREATE VIEW insights_insight_history_summary AS \
    SELECT max(ii.id) as id, \
        ii.user_id, \
        ii.insight_model_id, \
        count(ii.insight_model_id) as count_insights, \
        max(ii.created) as most_recent \
    FROM insights_insight ii \
    GROUP BY ii.insight_model_id, ii.user_id;"

    operations = [
        migrations.RunSQL(sql)
    ]