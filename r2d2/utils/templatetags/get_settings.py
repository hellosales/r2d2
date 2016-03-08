from django.conf import settings
from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError

register = Library()


class GetSettings(Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = settings
        return ''


@register.tag(name="get_settings")
def get_settings(parser, token):
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError("get_settings tag takes exactly 2 arguments")
    if bits[1] != 'as':
        raise TemplateSyntaxError("1st argument to get_settings tag must be 'as'")
    return GetSettings(bits[2])
