from django.contrib.sites.models import Site
from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError

register = Library()


class GetSite(Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = Site.objects.get_current()
        return ''


@register.tag(name="get_site")
def get_all_users(parser, token):
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError("get_site tag takes exactly 2 arguments")
    if bits[1] != 'as':
        raise TemplateSyntaxError("1st argument to get_site tag must be 'as'")
    return GetSite(bits[2])
