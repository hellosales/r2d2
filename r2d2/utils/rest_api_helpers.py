# -*- coding: utf-8 -*-
""" helpers for rest_framework API views """


class UserFilteredMixin(object):

    def get_queryset(self):
        queryset = super(UserFilteredMixin, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
