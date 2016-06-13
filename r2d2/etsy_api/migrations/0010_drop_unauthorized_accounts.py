# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def drop_unauthorized_accounts(apps, dummy_schema_editor):
    """ make all current accounts active & approved """
    etsy_cls = apps.get_model("etsy_api", "EtsyAccount")
    etsy_cls.objects.filter(access_token='fake_token').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('etsy_api', '0009_auto_20160613_1023'),
    ]

    operations = [
        migrations.RunPython(drop_unauthorized_accounts),
    ]
