import mock

from r2d2.data_importer.api import DataImporter
from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.test_utils import APIBaseTestCase
from rest_framework.reverse import reverse


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
        account = ShopifyStore.objects.create(user=self.user, access_token='token', name='name')
        not_authorized_account = ShopifyStore.objects.create(user=self.user, name='other-name')

        with mock.patch('r2d2.data_importer.tasks.fetch_data_task.apply_async') as mocked_fetch_data:
            mocked_fetch_data.return_value = None

            # run importer
            DataImporter.run_fetching_data()

            # check status #1
            self.assertEqual(ShopifyStore.objects.get(id=account.id).fetch_status, ShopifyStore.FETCH_SCHEDULED)

            # check status #2
            self.assertEqual(ShopifyStore.objects.get(id=not_authorized_account.id).fetch_status,
                             ShopifyStore.FETCH_IDLE)

        with mock.patch('r2d2.shopify_api.models.ShopifyStore._fetch_data_inner') as mocked_fetch_data_inner:
            mocked_fetch_data_inner.return_value = None

            account = ShopifyStore.objects.get(id=account.id)
            account.fetch_data()
            self.assertEqual(account.fetch_status, ShopifyStore.FETCH_SUCCESS)
            self.assertIsNotNone(account.last_successfull_call)
            mocked_fetch_data_inner.assert_any_call()

        with mock.patch('r2d2.shopify_api.models.ShopifyStore._fetch_data_inner') as mocked_fetch_data_inner:
            mocked_fetch_data_inner.return_value = None

            not_authorized_account = ShopifyStore.objects.get(id=not_authorized_account.id)
            not_authorized_account.fetch_data()
            self.assertEqual(not_authorized_account.fetch_status, ShopifyStore.FETCH_IDLE)
            mocked_fetch_data_inner.assert_not_called()

        # same check - but from different state
        with mock.patch('r2d2.data_importer.tasks.fetch_data_task.apply_async') as mocked_fetch_data:
            mocked_fetch_data.return_value = None

            DataImporter.run_fetching_data()
            self.assertEqual(ShopifyStore.objects.get(id=account.id).fetch_status, ShopifyStore.FETCH_SCHEDULED)

        # test if error is handled correctly
        with mock.patch('r2d2.shopify_api.models.ShopifyStore._fetch_data_inner') as mocked_fetch_data_inner:
            mocked_fetch_data_inner.side_effect = Exception('failed')

            account.fetch_status = ShopifyStore.FETCH_SCHEDULED
            account.fetch_data()

            account = ShopifyStore.objects.get(id=account.id)
            self.assertEqual(account.fetch_status, ShopifyStore.FETCH_FAILED)
            self.assertEqual(account.last_error, 'failed')


class DataImporterAccountsApiTestCase(APIBaseTestCase):
    """ tests creating & listing accounts through API """
    def setUp(self):
        self._create_user()

    def test_accounts_api(self):
        self._login()
        response = self.client.post(reverse('data-importer-accounts'),
                                    {"name": "other name", "class": "SquareupAccount"})
        self.assertEqual(response.status_code, 201)
        response = self.client.post(reverse('data-importer-accounts'),
                                    {"name": "other-name", "access_token": "token", "class": "ShopifyStore"})
        self.assertEqual(response.status_code, 201)
        response = self.client.post(reverse('data-importer-accounts'),
                                    {"name": "same-name", "access_token": "token", "class": "EtsyAccount"})
        self.assertEqual(response.status_code, 201)
        response = self.client.post(reverse('data-importer-accounts'),
                                    {"name": "same-name", "access_token": "token", "class": "ShopifyStore"})
        self.assertEqual(response.status_code, 201)

        response = self.client.get(reverse('data-importer-accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data[0]['class'], 'SquareupAccount')
        self.assertEqual(response.data[0]['name'], 'other name')
        self.assertEqual(response.data[1]['class'], 'ShopifyStore')
        self.assertEqual(response.data[1]['name'], 'other-name')
        self.assertEqual(response.data[2]['class'], 'EtsyAccount')
        self.assertEqual(response.data[2]['name'], 'same-name')
        self.assertEqual(response.data[3]['class'], 'ShopifyStore')
        self.assertEqual(response.data[3]['name'], 'same-name')

        account = response.data[0]
        response = self.client.get(reverse('data-importer-accounts'), {'class': account['class'], 'pk': account['pk']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['class'], 'SquareupAccount')
        self.assertEqual(response.data['name'], 'other name')

        response = self.client.put(reverse('data-importer-accounts'), {'name': account['name'], 'access_token': '',
                                                                       'class': account['class'], 'pk': account['pk']})
        self.assertEqual(response.status_code, 200)
