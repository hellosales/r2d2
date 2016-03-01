from django.contrib import admin

from r2d2.notifications.models import Notification, Category

admin.site.register(Notification)
admin.site.register(Category)
