# -*- coding: utf-8 -*-
""" Data Importer API
    - registers data provider models
    - runs data importing on registered models """
from datetime import timedelta
from django.utils.timezone import now

from r2d2.data_importer.serializers import DataImporterAccountSerializer
from r2d2.data_importer.tasks import fetch_data_task
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


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
    def _create_import_task(cls, model, pk):
        """ create celery task for data importer """
        model.objects.filter(pk=pk).update(fetch_status=model.FETCH_SCHEDULED, fetch_scheduled_at=now())
        fetch_data_task.apply_async(args=[model, pk], countdown=60)

    @classmethod
    def run_fetching_data(cls):
        """ creates tasks to import data """
        time_limit = now() - timedelta(days=1)
        for model in cls.__registered_models:
            query = model.objects.filter(fetch_status__in=(model.FETCH_IDLE, model.FETCH_SUCCESS),
                                         access_token__isnull=False).exclude(fetch_scheduled_at__gt=time_limit)
            pks = query.values_list('pk', flat=True)
            for pk in pks:
                cls._create_import_task(model, pk)


class DataImporterAccountsAPI(GenericAPIView):
    """ Allows to list, create & update data importer accounts.
        Account can be of one of following class: EtsyAccount, ShopifyStore, SquareupAccount """

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
            accounts.sort(key=lambda x: (x.name, x.__class__.__name__))

            serializer = DataImporterAccountSerializer(accounts, many=True)
            return Response(serializer.data)

    def post(self, request):
        """ Creates a new account.
            class -- required, account class
            name -- required, account name """
        model_class = DataImporter.get_model_by_name(request.data.get('class', None))
        if model_class:
            serializer = model_class.get_serializer()(data=request.data)
            if serializer.is_valid():
                serializer.save(user=self.request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """ Updates an account. In order to deactivate account, simply set access_token to null.
            class -- required, account class
            pk -- required, account pk """
        model_class = DataImporter.get_model_by_name(request.data.get('class', None))
        if model_class:
            try:
                instance = model_class.objects.get(pk=request.data.get('pk', None))
                serializer = model_class.get_serializer()(instance=instance, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except model_class.DoesNotExist:
                pass
        return Response(status=status.HTTP_400_BAD_REQUEST)
