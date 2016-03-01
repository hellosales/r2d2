# -*- coding: utf-8 -*-
from localflavor.us.forms import USZipCodeField
from django.db import models


class USZipModelField(models.CharField):

    description = "CharField with USPostalCodeField widget"

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': USZipCodeField}
        defaults.update(kwargs)
        return super(USZipModelField, self).formfield(**defaults)

#from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^r2d2\.accounts\.fields\.USZipModelField"])
