from django.conf import settings

from rest_framework import serializers

from r2d2.notifications.models import (
    Notification
)

from r2d2.utils.serializers import R2D2ModelSerializer

NOTIIFICATIONS_LIST_FIELDS = ['id', 'created', 'subject', 'category']

NOTIFICATIONS_FIELDS = NOTIIFICATIONS_LIST_FIELDS + ['content', 'url']


class NotificationsListSerializer(R2D2ModelSerializer):
    category = serializers.StringRelatedField()
    created = serializers.DateField(format=settings.DEFAULT_DATE_FORMAT)

    class Meta:
        model = Notification
        fields = NOTIIFICATIONS_LIST_FIELDS


class NotificationSerializer(NotificationsListSerializer):

    class Meta:
        model = Notification
        fields = NOTIFICATIONS_FIELDS
