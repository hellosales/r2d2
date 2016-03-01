# -*- coding: utf-8 -*-
from rest_framework.generics import RetrieveAPIView, ListAPIView

from django.utils.translation import ugettext_lazy as _

from r2d2.utils.api import BadRequestException

from r2d2.notifications.filters import NotificationsFilter

from r2d2.notifications.models import (
    Notification,
)

from r2d2.notifications.serializers import (
    NotificationsListSerializer, NotificationSerializer
)

from r2d2.notifications.permissions import HisOwnNotification


class NotificationsListApi(ListAPIView):
    """
    Get notifications list filtered by user - required. Only currently logged in user allowed.

    user -- user id
    """
    filter_class = NotificationsFilter
    queryset = Notification.objects.all()
    serializer_class = NotificationsListSerializer

    def get(self, request, *args, **kwargs):
        if not request.GET.get('user'):
            raise BadRequestException(_('Param user is required'))

        # check addintional conditions only for user other than self.
        if int(request.GET.get('user')) != request.user.pk:
            raise BadRequestException(_('You can only access your own notifications.'))

        response = super(NotificationsListApi, self).get(request, *args, **kwargs)
        return response


class NotificationsApi(RetrieveAPIView):
    """
    Get single notification for currently logged in user only

    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (HisOwnNotification,)

    def get_object(self):
        obj = super(NotificationsApi, self).get_object()
        obj.is_read = True
        obj.save()
        return obj
