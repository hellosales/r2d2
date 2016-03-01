# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django import forms


class YDForm():
    def change_required_message(self, *args, **kwargs):
        def get_field_name(field):
            if field.widget.attrs.get('placeholder'):
                return field.widget.attrs.get('placeholder')
            else:
                if field.label is None:
                    field.label = ""
                return "%s" % ''.join(field.label)

        for field in self.fields.values():
            field.error_messages['required'] = _('{fieldname} is required'.format(fieldname=get_field_name(field)))


class NonHTML5Fields():
    def change_fields_types(self, *args, **kwargs):
        field_types = ['email', 'number', 'range', 'date', 'url', 'number']
        for f in self.fields.values():
            if hasattr(f.widget, 'input_type') and f.widget.input_type in field_types:
                if f.widget.attrs is not None:
                    attrs = f.widget.attrs.copy()
                else:
                    attrs = {}
                f.widget = forms.TextInput(attrs=attrs)
