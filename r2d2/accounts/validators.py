# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from passwords.validators import validate_length, complexity


class PasswordValidator(object):
    message = _('Passwords must contain at least 8 digits and a number')
    code = "complexity"

    def __init__(self, min_length=None, max_length=None):
        pass

    def __call__(self, value):
        validators = [validate_length, complexity]
        for v in validators:
            try:
                v(value)
            except ValidationError:
                raise ValidationError(
                    self.message,
                    code=self.code)

password_validator = PasswordValidator()
