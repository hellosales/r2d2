""" squareup token refreshing """
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from r2d2.squareup_api.models import SquareupAccount


class Command(BaseCommand):
    """ Refresh squareup tokens that are close to expiration or are already expired """
    help = 'Refresh squareup tokens that are close to expiration or are already expired'

    def handle(self, *args, **options):
        time_limit = datetime.now() - timedelta(days=2)
        for sa in SquareupAccount.objects.filter(access_token__isnull=False, token_expiration__gte=time_limit):
            sa.refresh_token()
