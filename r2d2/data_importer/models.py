# -*- coding: utf-8 -*-
""" abstract data provider model """
from constance import config
from datetime import timedelta

from django import db
from django.conf import settings
from django.db import models, OperationalError
from django.db.models import Q
from django.utils import timezone
from django.utils.dateformat import DateFormat

from r2d2.accounts.models import Account
from r2d2.emails.send import send_email
from r2d2.insights.signals import data_fetched
from r2d2.utils.fields import JSONField


class AbstractDataProvider(models.Model):
    user = models.ForeignKey(Account)
    name = models.CharField(max_length=255, db_index=True)
    official_channel_name = None  # intended as official Hello Sales display name for channel
    access_token = models.CharField(max_length=255)
    authorization_date = models.DateTimeField()
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
    last_api_items_dates = JSONField(default={}, blank=True, help_text='used for querying API only for updates')
    is_active = models.BooleanField(default=True)

    OAUTH_ERROR = "There was a problem authorizing this channel. Please try again or contact Hello Sales."
    NAME_NOT_UNIQUE_ERROR = "Sorry, that Channel Name already exists. Please choose a different name for this Channel."
    MAX_RETRIES = settings.MAX_DATA_IMPORTER_RETRIES  # set this way as an override-able settings default

    class Meta:
        abstract = True
        unique_together = ('user', 'name')
        ordering = ('name', )

    @classmethod
    def get_serializer(cls):
        raise NotImplementedError

    @classmethod
    def get_fetch_data_task(cls):
        """
        Should return the task method (not class) for the specific data provider
        """
        raise NotImplementedError

    @classmethod
    def get_error_log_class(cls):
        raise NotImplementedError

    @classmethod
    def check_for_retry_errors(cls, response):
        """
        Checks the passed HTTP response for rate limiting and retriable errors.
        If found throws the appropriate exception.  If none found returns False.

        NOTE:  Each channel implementation of header info may be different so this
        should probably be overridden for each channel API implementation.

        """
        retry_time = None
        rate_limit = None
        if response.status_code == 429:
            if response.headers['x-ratelimit-limit']:
                rate_limit = response.headers['x-ratelimit-limit']
            if response.headers['x-rate-limit-limit']:
                rate_limit = response.headers['x-rate-limit-limit']

            re = RateLimitError('%d / %s' % (response.status_code, response.json().get('type', '')), rate_limit=rate_limit)
            raise re
        elif response.status_code >= 500:
            if response.headers['retry-after']:
                retry_time = response.headers['retry-after']

            re = RetriableError('%d / %s' % (response.status_code, response.json().get('type', '')), retry_time=retry_time)
            raise re

        return False

    def _fetch_data_inner(self):
        raise NotImplementedError

    def log_error(self, error, with_status=True):
        error_cls = self.get_error_log_class()
        error_cls.objects.create(account=self, error=error)

        if with_status:
            self.fetch_status = self.FETCH_FAILED
            self.save()

        # send email
        client_domain = config.CLIENT_DOMAIN
        bcc = config.ALERTS_RECEIVERS.split(',')
        protocol = 'https://' if getattr(settings, 'IS_SECURE', False) else 'http://'
        subject = 'Problem with your %s account on HelloSales' % self.name
        send_email('channel_problem', "%s <%s>" % (self.user.get_full_name(), self.user.email), subject,
                   {'protocol': protocol, 'client_domain': client_domain, 'account': self,
                    'account_class': self.__class__.__name__}, bcc=bcc)

    def fetch_data(self):
        """
        Entry point for call to remote channel API for data fetching.  Calls
        _fetch_data_inner() on child implementation to do channel-specific work.

        Because error conditions are specific to each channel this method should
        pass on exceptions thrown by _fetch_data_inner().  Error handling will
        be done in the calling method instead.  Currently error handling is only
        done in this method for status control.

        TODO:  re-evaluate logic around fetched_from_all and simplify if possible
        """
        from r2d2.data_importer.api import DataImporter

        if self.fetch_status != self.FETCH_SCHEDULED:
            return
        self.fetch_status = self.FETCH_IN_PROGRESS
        self.save()

        now = timezone.now()

        try:
            self._fetch_data_inner()
        except (RateLimitError, RetriableError) as re:
            self.fetch_status = self.FETCH_SCHEDULED
            self.save()
            raise re  # IMPORTANT!!

        self.fetch_status = self.FETCH_SUCCESS
        self.last_successfull_call = now

        # MySQL and Django interoperability bug kludge.  MySQL closes connections silently according to its wait_timeout
        # setting but if Django is mid-process it won't notice, though it respects its CONN_MAX_AGE setting.  This
        # affects us at transaction download here, so we check for the specific error then close the connection if
        # needed.  See https://code.djangoproject.com/ticket/21597
        try:
            self.save()
        except OperationalError as oe:
            if len(oe.args) == 2 and oe.args[0] == 2006 and oe.args[1] == 'MySQL server has gone away':
                db.connection.close()
                self.save()
            else:
                raise

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
    def next_sync(self):
        now = timezone.now()
        if self.is_active:  # show only for active channels
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
            dt = dt.astimezone(timezone.get_current_timezone())
            if dt.date() == now.astimezone(timezone.get_current_timezone()).date():
                return 'today ' + DateFormat(dt).format('@ g:i A')
            else:
                return 'tomorrow ' + DateFormat(dt).format('@ g:i A')
        else:
            return ''

    @property
    def last_updated(self):
        if self.last_successfull_call:
            return DateFormat(
                self.last_successfull_call.astimezone(timezone.get_current_timezone())
            ).format('n/j/Y @ g:i A')
        else:
            return ''


class SourceSuggestion(models.Model):
    user = models.ForeignKey(Account)
    text = models.TextField()


class AbstractErrorLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    error = models.TextField()
    error_description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def map_error(cls, error):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        if not self.error_description:
            self.error_description = self.map_error(self.error)
        return super(AbstractErrorLog, self).save(*args, **kwargs)


class RetriableError(Exception):
    """
    Indicates that the remote API call returned and error that we should retry
    the call later.  Allows a retry time to be set for access by the catcher.

    retry_time is in seconds
    """
    def __init__(self, msg, retry_time=None):
        super(RetriableError, self).__init__(msg)
        self.retry_time = retry_time


class RateLimitError(RetriableError):
    """
    Indicates that the remote API call returned and error that we should set
    rate limits on future calls.  Allows a rate limit to be set for access by the catcher.

    rate_limit is in calls per minute
    """
    def __init__(self, msg, rate_limit=None, retry_time=None):
        super(RateLimitError, self).__init__(msg, retry_time)
        self.rate_limit = rate_limit


def reconstitute_data_provider(name, pk):
    """
    Given a DataProvider name and pk will attempt to pull the record from the db
    """
    from r2d2.data_importer.api import DataImporter

    if not name or not pk:
        return None

    model = DataImporter.get_model_by_name(name)

    if model is None:
        return None

    di = model.objects.get(pk=pk)

    return di
