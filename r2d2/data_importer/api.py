# -*- coding: utf-8 -*-
""" Data Importer API
    - registers data provider models
    - runs data importing on registered models """


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
    def _create_import_task(cls, model, pk):
        """ create celery task for data importer """
        pass  # TODO

    @classmethod
    def run_import(cls):
        """ creates tasks to import data """
        for model in cls.__registered_models:
            pks = model.objects.filter(access_token__isnull=False).values_list('pk', flat=True)
            for pk in pks:
                cls._create_import_task(model, pk)
