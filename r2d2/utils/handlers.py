# -*- coding: utf-8 -*-
import hashlib

from time import sleep

from django.core.cache import cache
from django.core.files.uploadhandler import FileUploadHandler
from django.conf import settings

myip = lambda request: request.META.get('X-Forwarded-For',
                request.META['REMOTE_ADDR'])
cachekey = lambda req, prog_id: "{0}_{1}".format(myip(req),
                prog_id)
filehash = lambda filename: hashlib.md5(filename).hexdigest()


class UploadProgressCachedHandler(FileUploadHandler):
    """
        Tracks progress for file uploads.
        The http post request must contain a header or query parameter, 'X-Progress-ID'
        which should contain a unique string to identify the upload to be tracked.
        http://djangosnippets.org/snippets/678/
    """
    def __init__(self, request=None):
        super(UploadProgressCachedHandler, self).__init__(request)
        self.cache_key = None
        self.progress_id = None

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length
        if 'X-Progress-ID' in self.request.GET:
            self.progress_id = self.request.GET['X-Progress-ID']
        elif 'X-Progress-ID' in self.request.META:
            self.progress_id = self.request.META['X-Progress-ID']
        if self.progress_id:
            self.cache_key = cachekey(self.request, self.progress_id)
            cache.set(self.cache_key, {
                'length': self.content_length,
                'uploaded': 0
            })
        if settings.DEBUG_UPLOAD:
            sleep(3)

    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        if self.progress_id is None:
            self.progress_id = filehash(file_name)
        self.cache_key = cachekey(self.request, self.progress_id)
        cache.set(self.cache_key, {
                'length': self.content_length,
                'uploaded': 0
        })
        if settings.DEBUG_UPLOAD:
            sleep(3)

    def receive_data_chunk(self, raw_data, start):
        if self.cache_key:
            data = cache.get(self.cache_key)
            if data:
                data['uploaded'] += self.chunk_size
                cache.set(self.cache_key, data)
                if settings.DEBUG_UPLOAD:
                    sleep(3)
        return raw_data

    def file_complete(self, file_size):
        pass

    def upload_complete(self):
        if self.cache_key:
            cache.delete(self.cache_key)
