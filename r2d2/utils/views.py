# -*- coding: utf-8 -*-
from django.views.generic import View
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.views.defaults import page_not_found


class TestView(View):

    def get(self, request, **kwargs):
        return HttpResponse('Method: GET\n')

    def post(self, request, **kwargs):
        return HttpResponse('Method: POST\n')

    def put(self, request, **kwargs):
        return HttpResponse('Method: PUT\n')

    def delete(self, request, **kwargs):
        return HttpResponse('Method: DELETE\n')


def custom404(request, template_name='404.html'):
    path = request.get_full_path()
    split_path = path.split('?', 1)
    if not split_path[0].endswith('/'):
        # add back get params if needed
        if len(split_path) > 1:
            return HttpResponsePermanentRedirect(split_path[0] + '/?' + split_path[1])
        else:
            return HttpResponsePermanentRedirect(split_path[0] + '/')
    return page_not_found(request, template_name=template_name)
