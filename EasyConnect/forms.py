from django import forms
from EasyConnect.choices import STATE_CHOICES, GENDER_CHOICES
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from django.utils.translation import ugettext_lazy as _
import re
from datetime import datetime

class PatientForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control"}), max_length=200)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control"}), max_length=200)
    phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'class': "form-control form-control"}), max_length=10)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': "form-control form-control"}), max_length=200)
    dob = forms.CharField(widget=forms.DateInput(attrs={'class': "form-control half-width"}), max_length=200)
    gender = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': "form-check-input"}), choices=GENDER_CHOICES)
    address1 = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control"}), max_length=200)
    address2 = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control"}), max_length=200)
    city = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control"}), max_length=200)
    state = forms.ChoiceField(widget=forms.Select(attrs={'class': "btn btn-primary dropdown-toggle"}), choices=STATE_CHOICES)
    zip = forms.CharField(widget=forms.NumberInput(attrs={'class': "form-control form-control half-width"}), max_length=10)

    # pharmacy information
    location_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control half-width"}), max_length=200)
    pharmacy_phone = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control half-width"}), max_length=12)

    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        if not data:
            raise ValidationError(_('Invalid first name - cannot be blank'))

        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name']
        if not data:
            raise ValidationError(_('Invalid last name - cannot be blank'))

        return data

    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        if not data:
            raise ValidationError(_('Invalid phone number - cannot be blank'))

        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        if not data:
            raise ValidationError(_('Invalid e-mail - cannot be blank'))

        regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if not re.search(regex, data):
            raise ValidationError(_('Invalid e-mail - not a recognized e-mail address.'))

        return data

    def clean_dob(self):
        data = self.cleaned_data['dob']
        if not data:
            raise ValidationError(_('Invalid Birthday - cannot be blank'))

        # Check if a date is not in the past.
        if data > datetime.date.today():
            raise ValidationError(_('Invalid Birthday - date in the future'))

        return data

    def clean_gender(self):
        data = self.cleaned_data['gender']
        if not data:
            raise ValidationError(_('Invalid Gender - cannot be blank'))

        return data

    def clean_address1(self):
        data = self.cleaned_data['address1']
        if not data:
            raise ValidationError(_('Invalid Street Address - cannot be blank'))

        return data

    def clean_address2(self):
        data = self.cleaned_data['address2']

        return data

    def clean_city(self):
        data = self.cleaned_data['city']
        if not data:
            raise ValidationError(_('Invalid City - cannot be blank'))

        return data

    def clean_state(self):
        data = self.cleaned_data['state']
        if not data:
            raise ValidationError(_('Invalid State - cannot be blank'))

        return data

    def clean_zip(self):
        data = self.cleaned_data['zip']
        if not data:
            raise ValidationError(_('Invalid Zipcode - cannot be blank'))

        return data

    def clean_location_name(self):
        data = self.cleaned_data['location_name']
        if not data:
            raise ValidationError(_('Invalid Pharmacy location - cannot be blank'))

        return data

    def clean_phone(self):
        data = self.cleaned_data['pharmacy_phone']
        if not data:
            raise ValidationError(_('Invalid Pharmacy phone number - cannot be blank'))