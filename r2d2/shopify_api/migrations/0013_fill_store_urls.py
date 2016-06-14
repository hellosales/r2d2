# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_store_url_accounts(apps, dummy_schema_editor):
    """ make all current accounts active & approved """
    shopify_cls = apps.get_model("shopify_api", "ShopifyStore")
    for shop in shopify_cls.objects.all():
        shopify_cls.store_url = "%s.myshopify.com" % shop.name


class Migration(migrations.Migration):

    dependencies = [
        ('shopify_api', '0012_shopifystore_store_url'),
    ]

    operations = [
        migrations.RunPython(update_store_url_accounts),
    ]
