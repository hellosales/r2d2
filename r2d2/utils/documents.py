# -*- coding: utf-8 -*-
from django_mongoengine import document
from django_mongoengine import fields

from r2d2.accounts.models import Account
from django_mongoengine import mongo_admin


class StorageDynamicDocument(document.DynamicDocument):
    """ DynamicDocument for storing imported data
        once user_id / account_id is set it does not allow them to be changed """
    account_model = None
    prefix = None

    user_id = fields.IntField()
    account_id = fields.IntField(verbose_name='account id')

    meta = {'allow_inheritance': True}

    @classmethod
    def create_from_json(cls, account, json_data):
        new_obj = cls(user_id=account.user_id, account_id=account.id)
        for key, value in json_data.items():
            obj_key = key
            if hasattr(new_obj, key):
                obj_key = prefix + key
            setattr(new_obj, obj_key, value)
        return new_obj.save()

    def get_user(self):
        if not hasattr(self, '_get_user'):
            if self.user_id:
                try:
                    self._get_user = Account.objects.get(id=self.user_id)
                except Account.DoesNotExist:
                    self._get_user = '[deleted]'
            else:
                self._get_user = '[not set]'
        return self._get_user
    get_user.short_description = 'user'

    def get_account(self):
        assert self.account_model is not None
        if not hasattr(self, '_get_account'):
            if self.account_id:
                try:
                    self._get_account = self.account_model.objects.get(id=self.account_id)
                except self.account_model.DoesNotExist:
                    self._get_account = '[deleted]'
            else:
                self._get_account = '[not set]'
        return self._get_account
    get_account.short_description = 'account id'

    def __init__(self, *args, **kwargs):
        super(StorageDynamicDocument, self).__init__(*args, **kwargs)
        self.__orig_user_id = self.user_id
        self.__orig_account_id = self.account_id

    def save(self, *args, **kwargs):
        if self.__orig_user_id:
            self.user_id = self.__orig_user_id
        if self.__orig_account_id:
            self.account_id = self.__orig_account_id
        return super(StorageDynamicDocument, self).save()


class StorageDocumentAdmin(mongo_admin.JSONDocumentAdmin):
    def get_id(self, obj):
        return obj.id
    get_id.short_description = 'id'

    list_display = ['get_id', 'get_user', 'account_id']
