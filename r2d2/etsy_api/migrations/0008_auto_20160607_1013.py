# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_created(apps, dummy_schema_editor):
    schema_cls = apps.get_model("etsy_api", "EtsyAccount")
    for item in schema_cls.objects.all():
        if item.authorization_date:
            item.created = item.authorization_date
            item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('etsy_api', '0007_auto_20160607_1012'),
    ]

    operations = [
        migrations.RunPython(code=update_created),
    ]
