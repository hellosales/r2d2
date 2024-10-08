# -*- coding: utf-8 -*-
""" Data Importer API
    - registers data provider models
    - runs data importing on registered models """
from datetime import timedelta
from random import randint
import logging, traceback

from django.utils.timezone import now
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response

from r2d2.accounts.models import Account
from r2d2.accounts.permissions import IsSuperUser
from r2d2.data_importer.models import SourceSuggestion
from r2d2.data_importer.serializers import DataImporterAccountSerializer, SourceSuggestionSerializer
from r2d2.data_importer.tasks import monitor_rate_limit
from r2d2.utils.rest_api_helpers import UserFilteredMixin
from r2d2.utils.class_tools import name_for_class

logger = logging.getLogger('django')


class DataImporter(object):
    """ Data Importer """
    __registered_models = set([])

    @classmethod
    def register(cls, registered_model):
        """ adds model to the registered pool
            only registered models will be processed during data importing """
        assert hasattr(registered_model, 'fetch_data') and callable(registered_model.fetch_data)
        cls.__registered_models.add(registered_model)

    @classmethod
    def list_registered(cls):
        return {model.__name__ for model in cls.__registered_models}

    @classmethod
    def get_registered_models(cls):
        return (model for model in cls.__registered_models)

    @classmethod
    def get_model_by_name(cls, name):
        for model in cls.__registered_models:
            if model.__name__ == name:
                return model
        return None

    @classmethod
    def check_name_uniqeness(cls, user, name, instance):
        for model in cls.__registered_models:
            query = model.objects.filter(name=name, user=user)
            if instance and instance.__class__ == model:
                query = query.exclude(id=instance.id)
            if query.exists():
                return False
        return True

    @classmethod
    def create_import_task(cls, model, pk):
        """
        Create celery task for data importer.
        Put each task in a queue for that specific channel.  Note routing_key
        isn't needed if we create queues automatically.
        """
        model.objects.filter(pk=pk).update(fetch_status=model.FETCH_SCHEDULED, fetch_scheduled_at=now())
        model.get_fetch_data_task().apply_async(args=[pk],
                                                countdown=60 + randint(1, 200),
                                                queue=model.__name__)

    @classmethod
    def run_fetching_data(cls):
        """ creates tasks to import data """
        time_limit = now() - timedelta(days=1)
        for model in cls.__registered_models:
            query = model.objects.filter(user__approval_status=Account.APPROVED, user__is_active=True,
                                         is_active=True,
                                         fetch_status__in=(model.FETCH_IDLE, model.FETCH_SUCCESS, model.FETCH_FAILED),
                                         access_token__isnull=False).exclude(fetch_scheduled_at__gt=time_limit)
            pks = query.values_list('pk', flat=True)
            for pk in pks:
                cls.create_import_task(model, pk)

    @classmethod
    def monitor_queue_rate_limits(cls, worker, queue, task):
        """
        Launches a monitor to reset rate limits on the given queues, or on all queues if
        called with no arguments
        """
        monitor_rate_limit.apply_async(args=[worker, task],
                                       queue=queue)


class DataImporterAccountsAPI(GenericAPIView):
    """ Allows to list, create & update data importer accounts.
        Account can be of one of following class: EtsyAccount, ShopifyStore, SquareupAccount, StripeAccount  """

    def get(self, request):
        """ Gets list of accounts, or single account if class & pk is passed
            class -- optional, account class
            pk -- optional, account pk """
        # get all accounts for a logged in user
        model_class = DataImporter.get_model_by_name(request.query_params.get('class', None))
        pk = request.query_params.get('pk', None)
        if model_class and pk:
            try:
                obj = model_class.objects.get(pk=pk)
                serializer = DataImporterAccountSerializer(obj)
                return Response(serializer.data)
            except model_class.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            accounts = []
            for model in DataImporter.get_registered_models():
                accounts += list(model.objects.filter(user=request.user))

            # sort them by name
            accounts.sort(key=lambda x: (x.created, x.name, x.__class__.__name__), reverse=True)

            serializer = DataImporterAccountSerializer(accounts, many=True)
            return Response(serializer.data)

    def post(self, request):
        """ Creates a new account.
            class -- required, account class
            name -- required, account name
            oauth_callback_data -- required, custom for each account type (see dedicated serializers) """
        model_class = DataImporter.get_model_by_name(request.data.get('class', None))
        if model_class:
            serializer = model_class.get_serializer()(data=request.data, context=self.get_serializer_context())
            if serializer.is_valid():
                serializer.save(user=self.request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """ Updates an account..
            class -- required, account class
            pk -- required, account pk
            oauth_callback_data -- custom for each account type, only required if authorization is changed """
        model_class = DataImporter.get_model_by_name(request.data.get('class', None))
        if model_class:
            try:
                instance = model_class.objects.get(pk=request.data.get('pk', None))
                serializer = model_class.get_serializer()(instance=instance, data=request.data,
                                                          context=self.get_serializer_context())
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except model_class.DoesNotExist:
                raise
        return Response(status=status.HTTP_400_BAD_REQUEST)


class DataImporterGenerateOauthUrl(GenericAPIView):

    def post(self, request):
        """ Generates an oauth url for a given data importer class
            class -- required, account class
            shop_slug -- shop slug, required only for shopify """
        model_class = DataImporter.get_model_by_name(request.data.get('class', None))
        if model_class:
            serializer = model_class.get_oauth_url_serializer()(data=request.data,
                                                                context=self.get_serializer_context())
            if serializer.is_valid():
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SuggestionCreateAPI(UserFilteredMixin, CreateAPIView):
    """ API for creating source suggestions """
    serializer_class = SourceSuggestionSerializer
    queryset = SourceSuggestion.objects.all()


class DataImporterRunFetchingData(GenericAPIView):
    permission_classes = (IsSuperUser,)

    def get(self, request):
        try:
            DataImporter.run_fetching_data()
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)


class DataImporterMonitorRateLimits(GenericAPIView):
    permission_classes = (IsSuperUser,)

    def get(self, request):
        worker = request.query_params.get('worker', None)
        queue = request.query_params.get('queue', None)
        task = request.query_params.get('task', None)

        if not worker or not queue or not task:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            DataImporter.monitor_queue_rate_limits(worker, queue, task)
        except:
            logger.error(traceback.format_exc())
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)
