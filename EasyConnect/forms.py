from django import forms
from EasyConnect.choices import STATE_CHOICES, GENDER_CHOICES, DIAGNOSED_CHOICES
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from django.utils.translation import ugettext_lazy as _
import re
from datetime import date


class PatientForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                               'placeholder': 'First Name*'}), max_length=200)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                              'placeholder': 'Last Name*'}), max_length=200)
    phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                                  'placeholder': 'Phone*'}), max_length=12)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                           'placeholder': 'E-mail*'}), max_length=200)
    zip = forms.CharField(widget=forms.NumberInput(attrs={'class': "form-control form-control half-width",
                                                          'placeholder': 'Zip*'}), max_length=20)
    dob = forms.DateField(widget=forms.DateInput(attrs={'class': "form-control half-width",
                                                        'type': 'date',
                                                        'placeholder': 'mm/dd/yyyy'}))
    gender = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': "form-check-input"}),
                               choices=GENDER_CHOICES)
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': "form-check-input"}),
                             required=True)

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
        if data > date.today():
            raise ValidationError(_('Invalid Birthday - date in the future'))

        return data

    def clean_gender(self):
        data = self.cleaned_data['gender']
        if not data:
            raise ValidationError(_('Invalid Gender - cannot be blank'))

        return data

    def clean_zip(self):
        data = self.cleaned_data['zip']
        if not data:
            raise ValidationError(_('Invalid Zip code - cannot be blank'))

        return data


class SymptomsForm(forms.Form):
    symptom_description = forms.Textarea()
    allergies = forms.Textarea()
    medications = forms.Textarea()
    previous_diagnosis = forms.MultipleChoiceField(
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=DIAGNOSED_CHOICES
    )

    # pharmacy information
    location_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control half-width",
                                                                  'placeholder': 'Preferred Pharmacy Name*'}),
                                    max_length=200)
    pharmacy_phone = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control half-width",
                                                                   'placeholder': 'Preferred Pharmacy Phone*'}),
                                     max_length=12)

    def clean_symptom_description(self):
        data = self.cleaned_data['symptom_description']
        if not data:
            raise ValidationError(_('Invalid Symptom Description - cannot be blank'))

        return data

    def clean_allergies(self):
        data = self.cleaned_data['allergies']
        if not data:
            raise ValidationError(_('Invalid allergies - cannot be blank'))

        return data

    def clean_medications(self):
        data = self.cleaned_data['medications']
        if not data:
            raise ValidationError(_('Invalid medications - cannot be blank'))

        return data

    def clean_previous_diagnosis(self):
        data = self.cleaned_data['previous_diagnosis']
        if not data:
            raise ValidationError(_('Invalid previous diagnosis - cannot be blank'))

        return data

    def clean_location_name(self):
        data = self.cleaned_data['location_name']
        if not data:
            raise ValidationError(_('Invalid Pharmacy location - cannot be blank'))

        return data

    def clean_pharmacy_phone(self):
        data = self.cleaned_data['pharmacy_phone']
        if not data:
            raise ValidationError(_('Invalid Pharmacy phone number - cannot be blank'))

        return data