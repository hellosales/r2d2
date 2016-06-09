# from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.fields import DjangoValidationError
from rest_framework.fields import OrderedDict
from rest_framework.fields import SkipField
from rest_framework.fields import ValidationError
from rest_framework.fields import api_settings
from rest_framework.fields import empty
from rest_framework.fields import set_value
from rest_framework.serializers import get_validation_error_detail

from django.utils.translation import ugettext_lazy as _


class OneStepValidationSerializer(serializers.Serializer):
    """ Serializer designed all errors at single pass. Standard serializer first validates
        required fields and if any is missing it does not proceed any further with validation """

    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        if not isinstance(data, dict):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            })

        ret = OrderedDict()
        errors = OrderedDict()
        fields = self._writable_fields

        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = list(exc.messages)
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

        return ret, errors

    def run_validation(self, data=empty):
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        # mapping to internal values
        value, to_internal_errors = self.to_internal_value(data)

        # running validators
        validators_errors = OrderedDict()
        try:
            self.run_validators(value)
        except (ValidationError, DjangoValidationError) as exc:
            validators_errors = get_validation_error_detail(exc)

        # running final validation
        validation_errors = OrderedDict()
        try:
            value = self.validate(value)
            assert value is not None, '.validate() should return the validated data'
        except (ValidationError, DjangoValidationError) as exc:
            validation_errors = get_validation_error_detail(exc)

        # if there were any errors - raise the combination of them
        if to_internal_errors or validators_errors or validation_errors:
            # update dicts in reverse - to show most basic error for a given field if errors overlap
            validation_errors.update(validators_errors)
            validation_errors.update(to_internal_errors)
            raise ValidationError(detail=validation_errors)

        return value


class EmptySerializer(serializers.Serializer):
    pass


class R2D2Serializer(OneStepValidationSerializer):
    text = 'Fill in this field.'

    def __init__(self, *args, **kwargs):
        super(R2D2Serializer, self).__init__(*args, **kwargs)
        self.change_required_message()

    def change_required_message(self, *args, **kwargs):
        def get_field_name(key, field):
            return field.label if field.label else key.title()

        for key, field in self.fields.iteritems():
            if hasattr(field, 'error_messages'):
                field.error_messages['required'] = _(self.text)
                field.error_messages['blank'] = _(self.text)


class YDSerializer(serializers.Serializer):
    text = '{fieldname} is required'

    def __init__(self, *args, **kwargs):
        super(YDSerializer, self).__init__(*args, **kwargs)
        self.change_required_message()

    def change_required_message(self, *args, **kwargs):
        def get_field_name(key, field):
            return field.label if field.label else key.title()

        for key, field in self.fields.iteritems():
            if hasattr(field, 'error_messages'):
                field.error_messages['required'] = _(self.text.format(fieldname=unicode(get_field_name(key, field))))
                field.error_messages['blank'] = _(self.text.format(fieldname=unicode(get_field_name(key, field))))


class YDModelSerializer(YDSerializer, serializers.ModelSerializer):
    pass


class R2D2ModelSerializer(R2D2Serializer, serializers.ModelSerializer):
    pass


class RequestModelSerializer(YDModelSerializer):
    required_fields = []

    def get_fields(self):
        fields = super(RequestModelSerializer, self).get_fields()

        for f in self.required_fields:
            fields[f].required = True
            fields[f].allow_blank = False

        return fields

    def get_request_data(self):
        if self.context:
            return self.context['request'].data
        else:
            return {}
