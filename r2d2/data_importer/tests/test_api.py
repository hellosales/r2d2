import mock

from datetime import date
from datetime import timedelta
from freezegun import freeze_time

from django.utils import timezone

from r2d2.accounts.models import Account
from r2d2.data_importer.api import DataImporter
from r2d2.etsy_api.models import EtsyAccount
from r2d2.shopify_api.models import ShopifyErrorLog
from r2d2.shopify_api.models import ShopifyStore
from r2d2.squareup_api.models import SquareupAccount
from r2d2.utils.test_utils import APIBaseTestCase
from rest_framework.reverse import reverse


ERROR = "Not Found: https://fake.myshopify.com/admin/orders.json?status=any&limit=250"


class DataImporterApiTestCase(APIBaseTestCase):
    """ test if registering models work & if flow works correctly """
    def test_registering_models(self):
        """ simple checks registered models
            please add here models when a new data importer API is added"""

        registered_models = DataImporter.list_registered()
        self.assertIn('EtsyAccount', registered_models)
        self.assertIn('SquareupAccount', registered_models)
        self.assertIn('ShopifyStore', registered_models)

    def test_importer_flow(self):
        """ checks the whole importer flow
            - scheduling the idle task only if authorized
            - changing status after fetching data
            - rescheduling already completed tasks """
        self._create_user()
        self.user.approval_status = Account.APPROVED
        self.user.save()
        account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name',
                                              authorization_date=timezone.now())

        with mock.patch('r2d2.data_importer.tasks.fetch_data_task.apply_async') as mocked_fetch_data:
            mocked_fetch_data.return_value = None

            # run importer
            with freeze_time('2014-12-14'):
                DataImporter.run_fetching_data()

                store = ShopifyStore.objects.get(id=account.id)
                self.assertEqual(store.fetch_status, ShopifyStore.FETCH_SCHEDULED)
                self.assertEqual(store.fetch_scheduled_at.date(), date(year=2014, month=12, day=14))

        with mock.patch('r2d2.shopify_api.models.ShopifyStore._fetch_data_inner') as mocked_fetch_data_inner:
            mocked_fetch_data_inner.return_value = None

            account = ShopifyStore.objects.get(id=account.id)
            account.fetch_data()
            self.assertEqual(account.fetch_status, ShopifyStore.FETCH_SUCCESS)
            self.assertIsNotNone(account.last_successfull_call)
            mocked_fetch_data_inner.assert_any_call()

        # same check - but from different state
        with mock.patch('r2d2.data_importer.tasks.fetch_data_task.apply_async') as mocked_fetch_data:
            mocked_fetch_data.return_value = None

            with freeze_time('2014-12-14'):
                DataImporter.run_fetching_data()
                # too early - another fetching is not initiated
                self.assertEqual(ShopifyStore.objects.get(id=account.id).fetch_status, ShopifyStore.FETCH_SUCCESS)

            with freeze_time('2014-12-15'):
                # pretending the fetching was done one day earlier
                DataImporter.run_fetching_data()
                self.assertEqual(ShopifyStore.objects.get(id=account.id).fetch_status, ShopifyStore.FETCH_SCHEDULED)

        # test if error is handled correctly
        with mock.patch('r2d2.shopify_api.models.ShopifyStore._fetch_data_inner') as mocked_fetch_data_inner:
            mocked_fetch_data_inner.side_effect = Exception(ERROR)

            account.fetch_status = ShopifyStore.FETCH_SCHEDULED
            account.fetch_data()

            account = ShopifyStore.objects.get(id=account.id)
            self.assertEqual(account.fetch_status, ShopifyStore.FETCH_FAILED)
            self.assertEqual(ShopifyErrorLog.objects.filter(account=account).count(), 1)
            error = ShopifyErrorLog.objects.filter(account=account).first()
            self.assertEqual(error.error, ERROR)
            self.assertEqual(error.error_description, ("The requested resource could not be found but could be "
                                                       "available again in the future."))

    def test_importer_user_not_approved_flow(self):
        """ not approved flow """
        self._create_user()
        account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name',
                                              authorization_date=timezone.now())
        self.user.approval_status = Account.NOT_APPROVED
        self.user.save()

        with mock.patch('r2d2.data_importer.tasks.fetch_data_task.apply_async') as mocked_fetch_data:
            mocked_fetch_data.return_value = None

            # run importer
            with freeze_time('2014-12-14'):
                DataImporter.run_fetching_data()
                store = ShopifyStore.objects.get(id=account.id)
                self.assertEqual(store.fetch_status, ShopifyStore.FETCH_IDLE)

    def test_importer_not_active_accounts(self):
        """ dezactivated flow """
        self._create_user()
        account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name', is_active=False,
                                              authorization_date=timezone.now())

        with mock.patch('r2d2.data_importer.tasks.fetch_data_task.apply_async') as mocked_fetch_data:
            mocked_fetch_data.return_value = None

            # run importer
            with freeze_time('2014-12-14'):
                DataImporter.run_fetching_data()
                store = ShopifyStore.objects.get(id=account.id)
                self.assertEqual(store.fetch_status, ShopifyStore.FETCH_IDLE)

    def test_sending_signal_to_generators(self):
        self._create_user()
        account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name',
                                              authorization_date=timezone.now(), store_url='store_1')

        with mock.patch('r2d2.data_importer.tasks.fetch_data_task.apply_async') as mocked_fetch_data:
            mocked_fetch_data.return_value = None

            with mock.patch('r2d2.shopify_api.models.ShopifyStore._fetch_data_inner') as mocked_fetch_data_inner:
                mocked_fetch_data_inner.return_value = None

                with mock.patch('r2d2.insights.signals.data_fetched.send') as mocked_data_fetched:
                    with freeze_time('2014-12-14 1:00'):
                        DataImporter.run_fetching_data()
                        account = ShopifyStore.objects.get(id=account.id)
                        account.fetch_data()
                        self.assertEqual(account.fetch_status, ShopifyStore.FETCH_SUCCESS)
                        self.assertIsNotNone(account.last_successfull_call)
                        mocked_fetch_data_inner.assert_any_call()
                        mocked_data_fetched.assert_called_with(sender=None, account=account, fetched_from_all=True,
                                                               success=True)

                    with freeze_time('2014-12-14 2:00'):
                        account2 = ShopifyStore.objects.create(user=self.user, access_token='token', name='name2',
                                                               authorization_date=timezone.now(), store_url='store_2')
                        DataImporter.run_fetching_data()
                        account2 = ShopifyStore.objects.get(id=account2.id)
                        account2.fetch_data()
                        self.assertEqual(account2.fetch_status, ShopifyStore.FETCH_SUCCESS)
                        self.assertIsNotNone(account2.last_successfull_call)
                        mocked_fetch_data_inner.assert_any_call()
                        mocked_data_fetched.assert_called_with(sender=None, account=account2, fetched_from_all=False,
                                                               success=True)

                    with freeze_time('2014-12-15 1:00'):
                        DataImporter.run_fetching_data()
                        account = ShopifyStore.objects.get(id=account.id)
                        account.fetch_data()
                        self.assertEqual(account.fetch_status, ShopifyStore.FETCH_SUCCESS)
                        self.assertIsNotNone(account.last_successfull_call)
                        mocked_fetch_data_inner.assert_any_call()
                        mocked_data_fetched.assert_called_with(sender=None, account=account, fetched_from_all=False,
                                                               success=True)

                    with freeze_time('2014-12-15 2:00'):
                        DataImporter.run_fetching_data()
                        account2 = ShopifyStore.objects.get(id=account2.id)
                        account2.fetch_data()
                        self.assertEqual(account2.fetch_status, ShopifyStore.FETCH_SUCCESS)
                        self.assertIsNotNone(account2.last_successfull_call)
                        mocked_fetch_data_inner.assert_any_call()
                        mocked_data_fetched.assert_called_with(sender=None, account=account2, fetched_from_all=True,
                                                               success=True)


class DataImporterAccountsApiTestCase(APIBaseTestCase):
    """ tests creating & listing accounts through API """
    def setUp(self):
        self._create_user()

    def test_accounts_api(self):
        self._login()
        # test creating accounts
        # moved to respective tests for each data importer (since now it requires oauth authorization)
        SquareupAccount.objects.create(user=self.user, access_token='token', name='other name',
                                       authorization_date=timezone.now())
        ShopifyStore.objects.create(user=self.user, access_token='token', name='other-name',
                                    authorization_date=timezone.now(), store_url='test-1')
        EtsyAccount.objects.create(user=self.user, access_token='token', name='same-name',
                                   authorization_date=timezone.now())
        ShopifyStore.objects.create(user=self.user, access_token='token', name='not-the-same-name',
                                    authorization_date=timezone.now(), store_url='test-2')

        # test getting accounts list
        response = self.client.get(reverse('data-importer-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data[3]['class'], 'SquareupAccount')
        self.assertEqual(response.data[3]['name'], 'other name')
        square_account = response.data[3]
        self.assertEqual(response.data[2]['class'], 'ShopifyStore')
        self.assertEqual(response.data[2]['name'], 'other-name')
        shopify_account = response.data[2]
        self.assertEqual(response.data[1]['class'], 'EtsyAccount')
        self.assertEqual(response.data[1]['name'], 'same-name')
        etsy_account = response.data[1]
        self.assertEqual(response.data[0]['class'], 'ShopifyStore')
        self.assertEqual(response.data[0]['name'], 'not-the-same-name')

        # test getting single account
        account = response.data[0]
        response = self.client.get(reverse('data-importer-accounts'), {'class': account['class'], 'pk': account['pk']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['class'], 'ShopifyStore')
        self.assertEqual(response.data['name'], 'not-the-same-name')

        # test editing name - squareup
        square_account['name'] = 'new name'
        response = self.client.put(reverse('data-importer-accounts'), square_account)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'new name')

        # test editing name - etsy
        etsy_account['name'] = 'new name'
        response = self.client.put(reverse('data-importer-accounts'), etsy_account)
        self.assertEqual(response.status_code, 400)

        etsy_account['name'] = 'new name 2'
        response = self.client.put(reverse('data-importer-accounts'), etsy_account)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'new name 2')

        # test editing name - shopify
        shopify_account['name'] = 'new name'
        response = self.client.put(reverse('data-importer-accounts'), shopify_account)
        self.assertEqual(response.status_code, 400)

        shopify_account['name'] = 'new name 3'
        response = self.client.put(reverse('data-importer-accounts'), shopify_account)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'new name 3')

    @freeze_time('2014-12-15 01:00')
    def test_dates_serializing(self):
        """ test serializing is_active / next_sync / last_updated """

        # fresh account, not scheduled yet
        account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name',
                                              authorization_date=timezone.now())
        self._login()
        response = self.client.get(reverse('data-importer-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['is_active'], True)
        self.assertEqual(response.data[0]['next_sync'], 'today @ 1:05 AM')
        self.assertEqual(response.data[0]['last_updated'], '')

        # inactive account
        account.is_active = False
        account.save()
        response = self.client.get(reverse('data-importer-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['is_active'], False)
        self.assertEqual(response.data[0]['next_sync'], '')
        self.assertEqual(response.data[0]['last_updated'], '')

        # account currently fetching data
        account.is_active = True
        account.fetch_status = account.FETCH_IN_PROGRESS
        account.save()
        response = self.client.get(reverse('data-importer-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['is_active'], True)
        self.assertEqual(response.data[0]['next_sync'], 'now')
        self.assertEqual(response.data[0]['last_updated'], '')

        # account with past fetch data & successful call
        account.fetch_status = account.FETCH_SUCCESS
        account.last_successfull_call = account.fetch_scheduled_at = timezone.now() - timedelta(hours=12)
        account.save()
        response = self.client.get(reverse('data-importer-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['is_active'], True)
        self.assertEqual(response.data[0]['next_sync'], 'today @ 1:00 PM')
        self.assertEqual(response.data[0]['last_updated'], '12/14/2014 @ 1:00 PM')

        # account with past successful call & future fetch data
        account.fetch_scheduled_at = timezone.now() + timedelta(hours=24)
        account.save()
        response = self.client.get(reverse('data-importer-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['is_active'], True)
        self.assertEqual(response.data[0]['next_sync'], 'tomorrow @ 1:00 AM')
        self.assertEqual(response.data[0]['last_updated'], '12/14/2014 @ 1:00 PM')
