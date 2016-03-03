# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from filebrowser.sites import site

from r2d2.utils.views import TestView

admin.autodiscover()


urlpatterns = patterns(
    "",
    url(r"^$", TemplateView.as_view(template_name="index.html"), name="index"),
    url(r'', include('r2d2.accounts.urls')),
    url(r"^su/", include("django_su.urls")),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r"^js-tests/(?P<path>.*)", 'ydcommon.views.qunit_view', name='quinit'),
    url(r'^emails/', include('r2d2.emails.urls')),

    url(r"^admin/", include(admin.site.urls)),
    url(r"^api/", include('r2d2.api_urls')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),

    # oauth callbacks
    url(r'^shopify/', include('r2d2.shopify_api.urls')),

    (r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:],  # cut away leading slash
     'django.views.static.serve', {'document_root': settings.STATIC_ROOT,
                                   'show_indexes': True}),
    (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],  # cut away leading slash
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,
                                   'show_indexes': True}),

    (r'^grappelli/', include('grappelli.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    url(r"^test-cg0jfdnxn4em/$", csrf_exempt(TestView.as_view())),
    url(r'', include('basic_cms.urls')),
)

handler404 = 'r2d2.utils.views.custom404'

from r2d2.utils.storage import S3BotoStorageMixin
from django.core.files.storage import default_storage

if S3BotoStorageMixin not in default_storage.__class__.__bases__:
    default_storage.__class__.__bases__ += (S3BotoStorageMixin,)

site.storage = default_storage
