""" schedule fetching data """
from django.core.management.base import BaseCommand

from r2d2.data_importer.api import DataImporter


class Command(BaseCommand):
    """ Schedule data fetching for authrized accounts """
    help = 'Schedule data fetching for authrized accounts'

    def handle(self, *args, **options):
        DataImporter.run_fetching_data()
