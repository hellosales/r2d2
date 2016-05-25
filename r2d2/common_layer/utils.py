# -*- coding: utf-8 -*-


def map_id(account, value):
    """ ensure ID's are unique among different sources """
    return u"%s_%s_%s" % (account.__class__.__name__.lower(), account.id, unicode(value))
