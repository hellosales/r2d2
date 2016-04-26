# -*- coding: utf-8 -*-
from rest_framework.pagination import CursorPagination


class CursorByIDPagination(CursorPagination):
    page_size = 20
    ordering = '-id'
