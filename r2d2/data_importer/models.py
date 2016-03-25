# -*- coding: utf-8 -*-
""" abstract data provider model """
from django.db import models
from django.utils import timezone

from r2d2.accounts.models import Account
from r2d2.utils.fields import JSONField


class AbstractDataProvider(models.Model):
    user = models.ForeignKey(Account)
    name = models.CharField(max_length=255, db_index=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    authorization_date = models.DateTimeField(null=True, blank=True)
    last_successfull_call = models.DateTimeField(null=True, blank=True)

    FETCH_IDLE = "idle"
    FETCH_SCHEDULED = "scheduled"
    FETCH_IN_PROGRESS = "in progress"
    FETCH_FAILED = "failed"
    FETCH_SUCCESS = "success"
    FETCH_STATUS_CHOICES = (
        (FETCH_IDLE, "Idle"),
        (FETCH_SCHEDULED, "Scheduled"),
        (FETCH_IN_PROGRESS, "In progress"),
        (FETCH_FAILED, "Failed"),
        (FETCH_SUCCESS, "Success")
    )
    fetch_status = models.CharField(max_length=20, db_index=True, choices=FETCH_STATUS_CHOICES, default=FETCH_IDLE)
    last_error = models.TextField(null=True, blank=True)
    last_api_items_dates = JSONField(default={})

    class Meta:
        abstract = True
        unique_together = ('user', 'name')
        ordering = ('name', )

    API_MAPPING = {
        # 'model': (
        #     'endpoint': '...',
        #     'storage': MongoDocumentClassToStoreItIn
        # )
    }

    # def _fetch_item(self):


    def fetch_data(self):
        if self.fetch_status != self.FETCH_SCHEDULED:
            return
        self.fetch_status = self.FETCH_IN_PROGRESS
        self.save()

        for (key, value) in self.API_MAPPING.iteritems():
            last_item_date = self.last_api_items_dates.get(key, None)
            try:
                last_item_date = self._fetch_item(value['endpoint'], value['storage'], last_item_date)
                self.last_api_item_dates[key] = last_item_date
                self.last_successfull_call = timezone.now()
                self.save()
            except Exception, e:
                self.fetch_status = self.FETCH_FAILED
                self.last_error = unicode(e)
                self.save()
                return

        self.fetch_status = self.FETCH_SUCCESS
        self.save()

    @property
    def is_authorized(self):
        """ if token is set we assume account is authorized """
        return bool(self.access_token)
