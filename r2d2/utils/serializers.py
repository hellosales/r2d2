# from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from django.utils.translation import ugettext_lazy as _


class EmptySerializer(serializers.Serializer):
    pass


class R2D2Serializer(serializers.Serializer):
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
