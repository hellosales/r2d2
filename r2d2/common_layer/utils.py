# -*- coding: utf-8 -*-


def map_id(cls, value):
    """ ensure ID's are unique among different sources """
    return u"%s_%s" % (cls.__name__.lower(), unicode(value))
