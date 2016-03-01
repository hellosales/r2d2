from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.template import Library
from django.template import Node, TemplateSyntaxError
from django.utils.timezone import get_current_timezone
from django.template.defaultfilters import date
from django.conf import settings

register = Library()


class HoursMore(Node):
    def __init__(self, hours, string_format):
        self.hours = hours
        self.string_format = string_format

    def render(self, context):
        tzinfo = get_current_timezone() if settings.USE_TZ else None
        return date(datetime.now(tz=tzinfo) + relativedelta(hours=int(self.hours)), self.string_format).replace('"', '')


@register.tag(name="hours_more")
def hours_more(parser, token):
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError("hours_more tag takes exactly 2 arguments")
    return HoursMore(bits[1], bits[2])


class CountDate(Node):
    def __init__(self, start_date, operand, value, date_type, string_format, varname=None):
        if start_date == 'now':
            tzinfo = get_current_timezone() if settings.USE_TZ else None
            self.start_date = datetime.now(tz=tzinfo)
        else:
            self.start_date = datetime.datetime.strptime('start_date', "%Y-%m-%d").date()

        self.value = int(value)
        self.string_format = string_format
        self.varname = varname

        if (date_type in ['months', 'days', 'years', 'weeks']):
            self.type = date_type
        else:
            raise Exception('Incorrect value for count date type, it should be one of months, days, years, weeks')

        if operand in ['plus', 'minus']:
            self.operand = operand
        else:
            raise Exception('Incorrect value for coout date operand, it should be plus or minus (strings!)')

    def render(self, context):
        period = {self.type: self.value}
        if self.operand == 'plus':
            ret = date(self.start_date + relativedelta(**period), self.string_format).replace('"', '')
        else:
            ret = date(self.start_date - relativedelta(**period), self.string_format).replace('"', '')
        if self.varname:
            context[self.varname] = ret
        else:
            return ret


@register.tag(name="count_date")
def count_date(parser, token):
    """
        
        Return a date counted from given date.

        For example, to count today - 14 days:

            

        Possible choices are:
        - start_date: date in ISO format or now for today
        - operand: plus, minus
        - value: integer
        - type: days, weeks, months
        - string_format as described: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    """
    bits = token.split_contents()
    if len(bits) != 6 and len(bits) != 8:
        raise TemplateSyntaxError("count_date tag takes 5 or 6 arguments")
    if len(bits) == 6:
        return CountDate(bits[1], bits[2], bits[3], bits[4], bits[5])
    return CountDate(bits[1], bits[2], bits[3], bits[4], bits[5], bits[7])
