# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_account_merchant_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='approval_status',
            field=models.CharField(default=b'not approved', max_length=50, choices=[(b'not approved', b'Not Approved'), (b'approved', b'Approved'), (b'approval revoked', b'Approval Revoked')]),
        ),
        migrations.AlterField(
            model_name='account',
            name='is_active',
            field=models.BooleanField(default=True, help_text=b'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name=b'active'),
        ),
    ]
