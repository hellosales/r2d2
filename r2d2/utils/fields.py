# -*- coding: utf-8 -*-
import json
import base64
import zlib

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext_lazy as _
from django.forms import fields
from django.forms.utils import ValidationError as FormValidationError
from django.utils.text import compress_string
from django.db.models.signals import post_init
from django.core import exceptions


class JSONField(models.TextField):
    """JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly"""
    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase
    # Minimum length of value before compression kicks in
    compression_threshold = 64

    def __init__(self, verbose_name=None, json_type=None, compress=False, *args, **kwargs):
        self.json_type = json_type
        self.compress = compress
        super(JSONField, self).__init__(verbose_name, *args, **kwargs)

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""

        if isinstance(value, basestring):
            if self.compress and value.startswith('zlib;;'):
                value = zlib.decompress(base64.decodestring(value[6:]))

            try:
                value = json.loads(value)
            except ValueError:
                pass

        if self.json_type and not isinstance(value, self.json_type):
            raise exceptions.ValidationError(
                "%r is not of type %s (error occured when trying to access "
                "'%s.%s' field)" %
                (value, self.json_type, self.model._meta.db_table, self.name))
        return value

    def get_db_prep_save(self, value, connection):
        """Convert our JSON object to a string before we save"""

        if self.json_type and not isinstance(value, self.json_type):
            raise TypeError("%r is not of type %s" % (value, self.json_type))

        try:
            value = json.dumps(value)
        except TypeError, e:
            raise ValueError(e)

        if self.compress and len(value) >= self.compression_threshold:
            value = 'zlib;;' + base64.encodestring(zlib.compress(value))

        return super(JSONField, self).get_db_prep_save(value, connection=connection)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value

    def formfield(self, **kwargs):
        defaults = {'form_class': JSONFormField}
        defaults.update(kwargs)
        return super(JSONField, self).formfield(**defaults)


class JSONFormField(fields.CharField):
    def clean(self, value):

        if not value and not self.required:
            return None

        value = super(JSONFormField, self).clean(value)

        if isinstance(value, basestring):
            try:
                json.loads(value)
            except ValueError:
                raise FormValidationError(_("Enter valid JSON"))
        return value


class JSONFieldBase(models.Field):

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.dump_kwargs = kwargs.pop('dump_kwargs', {'cls': DjangoJSONEncoder})
        self.load_kwargs = kwargs.pop('load_kwargs', {})

        super(JSONFieldBase, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Convert string value to JSON"""
        if isinstance(value, basestring):
            try:
                return json.loads(value, **self.load_kwargs)
            except ValueError:
                pass
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        """Convert JSON object to a string"""

        if isinstance(value, basestring):
            return value
        return json.dumps(value, **self.dump_kwargs)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def value_from_object(self, obj):
        return json.dumps(super(JSONFieldBase, self).value_from_object(obj))

    def formfield(self, **kwargs):

        if "form_class" not in kwargs:
            kwargs["form_class"] = JSONFormField

        field = super(JSONFieldBase, self).formfield(**kwargs)

        if not field.help_text:
            field.help_text = "Enter valid JSON"

        return field


class JSONCharField(JSONFieldBase, models.CharField):
    """JSONCharField is a generic textfield that serializes/unserializes JSON objects,
    stored in the database like a CharField, which enables it to be used
    e.g. in unique keys"""


def uncompress_string(s):
    """helper function to reverse django.utils.text.compress_string"""
    import cStringIO
    import gzip
    try:
        val = s.encode('utf').decode('base64')
        zbuf = cStringIO.StringIO(val)
        zfile = gzip.GzipFile(fileobj=zbuf)
        ret = zfile.read()
        zfile.close()
    except:
        ret = s
    return ret


class CompressedTextField(models.TextField):
    """transparently compress data before hitting the db and uncompress after fetching"""

    def get_db_prep_save(self, value, connection):
        if value is not None:
            if isinstance(value, unicode):
                value = value.encode('utf8')
            value = compress_string(value)
            value = value.encode('base64').decode('utf8')
        return models.TextField.get_db_prep_save(self, value, connection=connection)

    def _get_val_from_obj(self, obj):
        if obj:
            value = uncompress_string(getattr(obj, self.attname))
            if value is not None:
                try:
                    value = value.decode('utf8')
                except UnicodeDecodeError:
                    pass
                return value
            else:
                return self.get_default()
        else:
            return self.get_default()

    def post_init(self, instance=None, **kwargs):
        value = self._get_val_from_obj(instance)
        if value:
            setattr(instance, self.attname, value)

    def contribute_to_class(self, cls, name):
        super(CompressedTextField, self).contribute_to_class(cls, name)
        post_init.connect(self.post_init, sender=cls)

    def get_internal_type(self):
        return "TextField"

    def db_type(self, **kwargs):
        from django.conf import settings
        db_types = {'django.db.backends.mysql': 'longblob', 'transaction_hooks.backends.mysql': 'longblob', 'django.db.backends.sqlite3': 'blob'}
        try:
            return db_types[settings.DATABASES['default']['ENGINE']]
        except KeyError:
            raise Exception('%s currently works only with: %s' % (self.__class__.__name__, ','.join(db_types.keys())))
