# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from r2d2.accounts.models import Account
from r2d2.accounts.forms import AdminPasswordChangeForm, AdminRegisterUserFullForm, AdminUserChangeForm


class AccountAdmin(UserAdmin):
    list_display = ('email',)
    ordering = ('email',)
    inlines = [
    ]
    form = AdminUserChangeForm
    readonly_fields = ('date_joined', )
    change_password_form = AdminPasswordChangeForm
    add_form = AdminRegisterUserFullForm
    search_fields = ('email',)
    fieldsets = ()
    exclude = ('username',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': AdminRegisterUserFullForm.Meta.fields,
        }),)

admin.site.register(Account, AccountAdmin)
