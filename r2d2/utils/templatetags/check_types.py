from django.template import Library

register = Library()


@register.filter(name="is_string")
def is_string(string):
    return isinstance(string, str) or isinstance(string, unicode)
