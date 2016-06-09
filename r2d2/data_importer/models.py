# -*- coding: utf-8 -*-
""" abstract data provider model """
from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.dateformat import DateFormat

from r2d2.accounts.models import Account
from r2d2.insights.signals import data_fetched
from r2d2.utils.fields import JSONField


class AbstractDataProvider(models.Model):
    user = models.ForeignKey(Account)
    name = models.CharField(max_length=255, db_index=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    authorization_date = models.DateTimeField(null=True, blank=True)
    last_successfull_call = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

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
    is_active = models.BooleanField(default=True)

    OAUTH_ERROR = "There was a problem authorizing this channel. Please try again or contact Hello Sales."
    NAME_NOT_UNIQUE_ERROR = "Sorry, that Channel Name already exists. Please choose a different name for this Channel."

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

        now = timezone.now()
        try:
            self._fetch_data_inner()
            self.fetch_status = self.FETCH_SUCCESS
            self.last_successfull_call = now
        except:
            # "try twice"
            try:
                self._fetch_data_inner()
                self.fetch_status = self.FETCH_SUCCESS
                self.last_successfull_call = now
            except Exception, e:
                self.fetch_status = self.FETCH_FAILED
                self.last_error = unicode(e)
        self.save()

        # send out signal
        success = self.fetch_status == self.FETCH_SUCCESS
        fetched_from_all = not self.user.last_fetched_all or self.user.last_fetched_all.date() < now.date()
        if fetched_from_all:
            date_from = now - timedelta(hours=24)
            date_to = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                      microseconds=now.microsecond)
            date_range = (date_from, date_to)
            query = Q(user__id=self.user_id) & (Q(fetch_status__in=(self.FETCH_SCHEDULED, self.FETCH_IN_PROGRESS)) |
                                                Q(access_token__isnull=False, fetch_scheduled_at__range=date_range))
            for importer_class in DataImporter.get_registered_models():
                if importer_class.objects.filter(query).exists():
                    fetched_from_all = False
        data_fetched.send(sender=None, account=self, success=success, fetched_from_all=fetched_from_all)

        if fetched_from_all and success:
            self.user.last_fetched_all = now
            self.user.save()

    @property
    def is_authorized(self):
        """ if token is set we assume account is authorized """
        return bool(self.access_token)

    @property
    def next_sync(self):
        now = timezone.now()
        if self.is_active and self.is_authorized:  # show only for active channels
            if self.fetch_status == self.FETCH_IN_PROGRESS:
                return 'now'
            if self.fetch_scheduled_at:
                # it is already scheduled for the future - so just show it
                if self.fetch_scheduled_at > now:
                    dt = self.fetch_scheduled_at
                # it was queried in past 24h - it will be repeated after 24 hours from last pull
                elif self.fetch_scheduled_at > now - timedelta(hours=24):
                    dt = self.fetch_scheduled_at + timedelta(hours=24)
                # it was queried in the further past - it probably got activated recently - show next 5 minutes
                else:
                    dt = now + timedelta(minutes=5)
            # new account - just show next 5 minutes
            else:
                dt = now + timedelta(minutes=5)
            if dt.date() == now.date():
                return 'today ' + DateFormat(dt).format('@ g:i A')
            else:
                return 'tomorrow ' + DateFormat(dt).format('@ g:i A')
        else:
            return ''

    @property
    def last_updated(self):
        if self.last_successfull_call:
            return DateFormat(self.last_successfull_call).format('n/j/Y @ g:i A')
        else:
            return ''


class SourceSuggestion(models.Model):
    user = models.ForeignKey(Account)
    text = models.TextField()
