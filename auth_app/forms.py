from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from store.models import Customer

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    contact_number = forms.CharField(max_length=12, required=True)

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if not contact_number.isdigit():
            raise ValidationError('Contact number must be digits only.')
        if len(contact_number) < 10 or len(contact_number) > 12:
            raise ValidationError('Contact number must be between 10 and 12 digits.')
        if Customer.objects.filter(contact_number=contact_number).exists():
            raise ValidationError('This contact number is already registered.')
        return contact_number

from django import forms

class LoginForm(forms.Form):
    contact_number = forms.CharField(max_length=12)

class SuperuserPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
