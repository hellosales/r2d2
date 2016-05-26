# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def adjust_state(apps, dummy_schema_editor):
    """ make all current accounts active & approved """
    account_cls = apps.get_model("accounts", "Account")
    account_cls.objects.all().update(is_active=True, approval_status="approved")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20160526_0623'),
    ]

    operations = [
        migrations.RunPython(adjust_state),
    ]
