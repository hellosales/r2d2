# -*- coding: utf-8 -*-
""" tests for basic functionality of common layer - creating & updating objects on signals """
from datetime import datetime
from datetime import timedelta
from freezegun import freeze_time

from r2d2.common_layer.models import CommonTransaction
from r2d2.common_layer.signals import object_imported
from r2d2.etsy_api.models import EtsyAccount
from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.test_utils import APIBaseTestCase


class TestBase(APIBaseTestCase):
    """ test basic common layer functionality """

    def _get_sample_transaction(self, transaction_id, date):
        return {
            'user_id': 1,
            'transaction_id': transaction_id,
            'date': date,
            'products': [{
                'name': "test",
                'sku': "whateva",
                'quantity': 1,
                'price': 10.0,
                'tax': 1.0,
                'discount': 2.0,
                'total': 9.0
            }],
            'total_price': 10.0,
            'total_tax': 1.0,
            'total_discount': 2.0,
            'total_total': 9.0,
        }

    def setUp(self):
        self._create_user()

    def tearDown(self):
        CommonTransaction.objects.all().delete()

    @freeze_time('2016-08-28')
    def test_all(self):
        """ - Test creating object on signal
            - Test updating object on signal
            - Test if there is no collision for objects with same ID but different sources """

        now = datetime.now()

        # test creating object on signal
        self.assertEqual(CommonTransaction.objects.count(), 0)
        sample_object = self._get_sample_transaction(1, now)
        object_imported.send(sender=None, importer_class=ShopifyStore, mapped_data=sample_object)
        self.assertEqual(CommonTransaction.objects.count(), 1)

        # test updating object on signal
        sample_object = self._get_sample_transaction(1, now + timedelta(days=1))
        object_imported.send(sender=None, importer_class=ShopifyStore, mapped_data=sample_object)
        self.assertEqual(CommonTransaction.objects.count(), 1)
        common_transaction = CommonTransaction.objects.all()[0]
        self.assertEqual(common_transaction.date, now + timedelta(days=1))
        self.assertEqual(common_transaction.source, "ShopifyStore")

        # test if there is no collision for objects with same ID but different sources
        sample_object = self._get_sample_transaction(1, now)
        object_imported.send(sender=None, importer_class=EtsyAccount, mapped_data=sample_object)
        self.assertEqual(CommonTransaction.objects.count(), 2)

        # sanity check
        sample_object = self._get_sample_transaction(2, now)
        object_imported.send(sender=None, importer_class=ShopifyStore, mapped_data=sample_object)
        self.assertEqual(CommonTransaction.objects.count(), 3)
