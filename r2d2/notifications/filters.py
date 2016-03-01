import django_filters

from r2d2.notifications.models import (
    Notification
)


class NotificationsFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(name="user", required=True)

    class Meta:
        model = Notification
        fields = ['user']
