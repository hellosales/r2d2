from django.conf import settings

from r2d2.celery import app
from r2d2.data_importer.tasks import BaseImporterTask
from r2d2.stripe_api.models import StripeAccount
from r2d2.utils.class_tools import name_for_class


class StripeImporterTask(BaseImporterTask):
    """
    Stripe class for data importer task.  Defined here only to allow independent task
    naming as a Celery implementation detail.
    """
    rate_limit = settings.STRIPE_RATE_LIMIT


@app.task(bind=True, base=StripeImporterTask)
def fetch_data(self, pk, rate=None):
    return self._run_inner(name_for_class(StripeAccount), pk, rate)
