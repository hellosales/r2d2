# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.conf import settings
from django.template import loader
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.forms import AdminPasswordChangeForm as DjagnoAdminPasswordChangeForm, \
    SetPasswordForm, PasswordChangeForm, ReadOnlyPasswordHashField, \
    AuthenticationForm as DjangoAuthenticationForm, PasswordResetForm as DjangoPasswordResetForm

from passwords.fields import PasswordField

from r2d2.accounts.validators import password_validator
from r2d2.accounts.models import Account
from r2d2.emails.send import send_email

from r2d2.utils.forms import YDForm, NonHTML5Fields


def get_user_by_email(email):
    users = Account.objects.all().only('email', 'id', 'is_active')
    for user in users:
        if user.email == email:
            return user


class ValidatingSetPasswordForm(YDForm, SetPasswordForm):
    new_password1 = forms.CharField(label=_(""),
                                    widget=forms.PasswordInput(attrs={'placeholder': 'Choose A Password'}),
                                    help_text=_("Password must be at least 8 characters and include a number."),
                                    validators=[password_validator])
    new_password2 = forms.CharField(label=_(""),
                                    widget=forms.PasswordInput(attrs={
                                        'placeholder': 'Password Confirmation'}),
                                    validators=[password_validator])

    def __init__(self, *args, **kwargs):
        super(ValidatingSetPasswordForm, self).__init__(*args, **kwargs)
        self.change_required_message()

    def clean_new_password2(self):
        return self.cleaned_data.get('new_password2')

    def clean(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get('new_password1')
        password_confirm = cleaned_data.get('new_password2')
        if password != password_confirm:
            raise forms.ValidationError(_("Passwords do not match"))
        return cleaned_data

    def save(self, commit=True):
        super(ValidatingSetPasswordForm, self).save(commit=commit)
        return self.user


class ValidatingPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(label=_(""),
                                    help_text=_("Password must be at least 8 characters and include a number."),
                                    widget=forms.PasswordInput(attrs={'placeholder': 'Choose A Password'}),
                                    validators=[password_validator])
    new_password2 = forms.CharField(label=_(""),
                                    widget=forms.PasswordInput(attrs={'placeholder': 'Choose A Password'}),
                                    validators=[password_validator])


class AdminPasswordChangeForm(DjagnoAdminPasswordChangeForm):
    password1 = PasswordField(label=_("New password"))
    password2 = PasswordField(label=_("New password confirm"))


class RegisterUserFullForm(forms.ModelForm, YDForm, NonHTML5Fields):
    password = forms.CharField(label=_(""), widget=forms.PasswordInput(attrs={'placeholder': 'Choose A Password'}),
                               help_text=_("Password must be at least 8 characters and include a number."),
                               validators=[password_validator])
    password_confirm = forms.CharField(label=_(""),
                                       widget=forms.PasswordInput(attrs={'placeholder': 'Password Confirmation'}),
                                       validators=[password_validator])

    def __init__(self, *args, **kwargs):
        super(RegisterUserFullForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            Account.objects.get(email=email)
            raise forms.ValidationError(mark_safe(
                _('This email is already in use. <a href="%s">Click here</a> to reset your password')
                % reverse('password_reset')))
        except Account.DoesNotExist:
            return email

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError(_("Passwords do not match"))
        return password_confirm

    def save(self, **kwargs):
        self.instance.set_password(self.cleaned_data['password'])
        return super(RegisterUserFullForm, self).save(**kwargs)

    class Meta:
        model = Account
        fields = ['email', 'password', 'password_confirm', ]


class AdminRegisterUserFullForm(RegisterUserFullForm):
    # small hack to show those fields
    # agree_to_terms_conditions = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super(AdminRegisterUserFullForm, self).__init__(*args, **kwargs)
        # self.fields['agree_to_terms_conditions'].required = False

    def clean(self):
        cleaned_data = self.cleaned_data
        # cleaned_data['agree_to_terms_conditions'] = True
        return cleaned_data


class AuthenticationForm(DjangoAuthenticationForm, YDForm, NonHTML5Fields):

    def __init__(self, request=None, *args, **kwargs):
        super(AuthenticationForm, self).__init__(request=request, *args, **kwargs)
        self.change_fields_types()
        self.fields['username'].widget = forms.EmailInput()
        self.fields['username'].widget.attrs['placeholder'] = 'Email'
        self.fields['username'].label = ''
        self.error_messages['invalid_login'] = _(u"Your email or password is incorrect")
        self.fields['password'].widget.attrs['placeholder'] = 'Password'
        self.fields['password'].label = ''
        self.change_required_message()


class PasswordResetForm(YDForm, DjangoPasswordResetForm, NonHTML5Fields):

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.change_fields_types()
        self.fields['email'].widget.attrs['placeholder'] = 'Your registered email'
        self.fields['email'].label = ''
        self.fields['email'].required = True
        self.change_required_message()

    def clean(self):
        """
        Validates that an active user exists with the given email address.
        """
        cleaned_data = self.cleaned_data
        email = cleaned_data.get("email")
        if email:
            email = email.lower()
            user = get_user_by_email(email)
            self.users_cache = [user]
            try:
                url = reverse('signup')
            except NoReverseMatch:
                url = '#'
            unknown_user_error = mark_safe(_(
                'There is no account with that email address. <br/> <a href="{url}">Sign up</a> for r2d2.'
                .format(url=url)))
            self.users_cache = [user]
            if not user:
                raise forms.ValidationError(unknown_user_error)
            if not any(user.is_active for user in self.users_cache):
                # none of the filtered users are active
                raise forms.ValidationError(unknown_user_error)
            if any((not user.has_usable_password())
                   for user in self.users_cache):
                raise forms.ValidationError(unknown_user_error)
        return cleaned_data

    def save(self, domain_override=None,
             subject_template_name='emails/resetPassword/subject.txt',
             email_template_name='emails/resetPassword/content.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'STATIC_URL': settings.STATIC_URL,
                'user': user,
                'site': current_site,
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(str(user.id)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            subject = ''.join(subject.splitlines())
            send_email('reset_password', user.email, subject, c)


class AdminUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = Account
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AdminUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
