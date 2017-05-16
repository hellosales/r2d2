from __future__ import absolute_import
from django.conf import settings
from r2d2.celery import app
from r2d2.data_importer.tasks import BaseImporterTask
from r2d2.shopify_api.models import ShopifyStore
from r2d2.utils.class_tools import name_for_class


class ShopifyImporterTask(BaseImporterTask):
    """
    Shopify class for data importer task.  Defined here only to allow independent task
    naming as a Celery implementation detail.
    """

    rate_limit = settings.SHOPIFY_RATE_LIMIT

    def rate_backoff(self, rate):
        """
        Returns the rate to execute tasks at, per 60 seconds

        Uses the inverse exponential rate strategy.
        """
        if rate:
            return min(rate/2, self.rate_limit)
        else:
            return self.rate_limit


@app.task(bind=True, base=ShopifyImporterTask)
def fetch_data(self, pk, rate=None):
    return self._run_inner(name_for_class(ShopifyStore), pk, rate)
