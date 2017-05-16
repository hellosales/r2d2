# -*- coding: utf-8 -*-
""" insights models """
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

from r2d2.accounts.models import Account
from r2d2.insights.generators import InsightDispatcher
from r2d2.insights.signals import data_fetched
from r2d2.insights.signals import insight_post_save


IMAGE_CONTENT_TYPES = set([
    'image/pjpeg',
    'image/jpeg'
])

ALLOWED_CONTENT_TYPES = set([
    'application/vnd.ms-excel',
    'application/excel',
    'application/x-msexcel',
    'application/x-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
    'application/vnd.ms-excel.sheet.macroEnabled.12',  # .xlsm
    'application/vnd.ms-excel.sheet.binary.macroEnabled.12',  # .xlsb
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'application/vnd.ms-word.document.macroEnabled.12',  # .docm
    'text/plain',
    'text/csv',
]) | IMAGE_CONTENT_TYPES


class Insight(models.Model):
    """
    model to store served insights
    """
    user = models.ForeignKey(Account, limit_choices_to={"approval_status": Account.APPROVED, 'is_active': True})
    created = models.DateTimeField(default=timezone.now)
    text = models.TextField()
    generator_class = models.CharField(max_length=100, editable=False)
    is_initial = models.BooleanField()  # whether this was the initial insight for this user
    time_period = models.CharField(max_length=100, editable=False)
    insight_model_id = models.IntegerField()
    was_helpful = models.NullBooleanField()  # whether the user voted helpful or unhelpful

    # The DataProvider that triggered the Insight to fire
    # These two fields allow us to do a DB lookup for the AbstractDataProvider subclass.
    # TODO: modify this if this is managed more flexibly through the DB later
    data_provider_name = models.CharField(max_length=200, editable=False)
    data_provider_id = models.IntegerField()


class Product(models.Model):
    """
    A product
    """
    insight = models.ForeignKey(Insight)
    sku = models.CharField(max_length=500)
    name = models.CharField(max_length=500)


class Channel(models.Model):
    """
    The channel referenced in the Insight, which may be different than the channel
    that caused the Insight to fire.
    A DataProvider encapsulation that allows us to trap source info for Insights.
    This is meant to allow us to know which Channels were discussed in an Insight.
    Name is name of the Channel in the Insight, NOT DataProvider of pulled from
    to generate the Insight
    TODO:  modify this if the different data providers are managed more flexibly
        as data via the DB instead of as separate apps in Django
    """
    insight = models.ForeignKey(Insight)

    # These two fields allow us to do a DB lookup for the AbstractDataProvider subclass.
    # TODO: modify this if this is managed more flexibly through the DB later
    data_provider_name = models.CharField(max_length=200, editable=False)
    data_provider_id = models.IntegerField()


class InsightHistorySummary(models.Model):
    """
    Unmanaged model for the insights_insight_history_summary view that summarizes
    how many of each InsightModel have been served, and what the most recent date
    is for each
    """
    id = models.IntegerField(primary_key=True)  # Placeholder id only, not meaningful
    user = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    insight_model_id = models.IntegerField()
    count_insights = models.IntegerField()
    most_recent = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'insights_insight_history_summary'


def validate_file_extension(value):
    """ The file formats accepted should include excel files, csv files, word docs, .txt files, and .jpg files. """
    if not hasattr(value.file, 'content_type'):  # FIXME: detect edit
        return

    if value.file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(u'Files allowed: word, excel, csv, text and jpg. Current file detected as %s' %
                              value.file.content_type)


class InsightAttachment(models.Model):
    """ attachment for insight """
    insight = models.ForeignKey(Insight, related_name='attachments')
    content_type = models.CharField(max_length=50, null=True, editable=True)
    file = models.FileField(upload_to='insights_attachments', validators=[validate_file_extension])

    @property
    def is_image(self):
        return self.content_type in IMAGE_CONTENT_TYPES

    @property
    def file_name(self):
        if not self.file or not self.file.name:
            return ''
        return self.file.name.rsplit('/')[1]

    def save(self, *args, **kwargs):
        if self.file and self.file.file and hasattr(self.file.file, 'content_type'):
            self.content_type = self.file.file.content_type
        return super(InsightAttachment, self).save(*args, **kwargs)


post_save.connect(insight_post_save, sender=Insight)

# IMPORTANT! order of connect will be the order of insights
data_fetched.connect(InsightDispatcher.handle_data_fetched)
