# -*- coding: utf-8 -*-
'''
Utility functions for the common_layer
'''


def nearest(desired, options):
    """
    From the list, picks the option nearest to the number or date

    desired:  the number or date you'd like to be close to
    options:  the list of options from which to pick the nearest option

    from:  http://stackoverflow.com/questions/32237862/find-the-closest-date-to-a-given-date
    """
    return min(options, key=lambda x: abs(x - desired))


def map_id(account, value):
    """ ensure ID's are unique among different sources """
    return u"%s_%s_%s" % (account.__class__.__name__.lower(), account.id, unicode(value))
