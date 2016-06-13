# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def drop_unauthorized_accounts(apps, dummy_schema_editor):
    """ make all current accounts active & approved """
    squareup_cls = apps.get_model("squareup_api", "SquareupAccount")
    squareup_cls.objects.filter(access_token='fake_token').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('squareup_api', '0013_auto_20160613_1023'),
    ]

    operations = [
        migrations.RunPython(drop_unauthorized_accounts),
    ]
