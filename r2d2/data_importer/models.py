# -*- coding: utf-8 -*-
""" abstract data provider model """
from django.db import models
from django.utils.timezone import now

from r2d2.accounts.models import Account
from r2d2.insights.signals import data_fetched
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
    fetch_scheduled_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(null=True, blank=True)
    last_api_items_dates = JSONField(default={}, blank=True, help_text='used for querying API only for updates')

    class Meta:
        abstract = True
        unique_together = ('user', 'name')
        ordering = ('name', )

    @classmethod
    def get_serializer(cls):
        raise NotImplementedError

    def _fetch_data_inner(self):
        raise NotImplementedError

    def fetch_data(self):
        from r2d2.data_importer.api import DataImporter

        if self.fetch_status != self.FETCH_SCHEDULED:
            return
        self.fetch_status = self.FETCH_IN_PROGRESS
        self.save()

        try:
            self._fetch_data_inner()
            self.fetch_status = self.FETCH_SUCCESS
            self.last_successfull_call = now()
        except Exception, e:
            self.fetch_status = self.FETCH_FAILED
            self.last_error = unicode(e)
        self.save()

        # send out signal
        success = self.fetch_status == self.FETCH_SUCCESS
        fetched_from_all = True
        for importer_class in DataImporter.get_registered_models():
            if importer_class.objects.filter(user__id=self.user_id,
                                             fetch_status__in=(self.FETCH_SCHEDULED, self.FETCH_IN_PROGRESS)).exists():
                fetched_from_all = False
            # TODO: make sure we call fetched_from_all only once per day 1) after the last import, 2) once it was
            # called it should not be called anymore that day ()
            # - solutions - set cache 24h
            # - add date to user account & move it to cron [remove fetched from all}
            # - combination of current + date in profile
        data_fetched.send(sender=None, account=self, success=success, fetched_from_all=fetched_from_all)

    @property
    def is_authorized(self):
        """ if token is set we assume account is authorized """
        return bool(self.access_token)


class SourceSuggestion(models.Model):
    user = models.ForeignKey(Account)
    text = models.TextField()
