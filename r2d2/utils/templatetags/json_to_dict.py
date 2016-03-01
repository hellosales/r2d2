from json import loads

from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()


@stringfilter
def json_to_dict(string):
    """
    Return a dict from json

    For example, to re-display a date string in another format (uncomment):

        

    """
    try:
        return loads(string)
    except ValueError:
        return None

register.filter(json_to_dict)
