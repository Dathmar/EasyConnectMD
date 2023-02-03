from django import forms
from EasyConnect.choices import GENDER_CHOICES, DIAGNOSED_CHOICES
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
import re
from datetime import date
from EasyConnect.models import Icd10


class PatientForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

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
                                                        'onChange': 'checkAge(this.value);',
                                                        'placeholder': 'mm/dd/yyyy'}))
    gender = forms.ChoiceField(widget=forms.RadioSelect(),
                               choices=GENDER_CHOICES)
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': "form-check-input"}),
                             label='I agree to the Terms of Service',
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

        # deactivating this section of code to allow younger than 18 with parent's permission.
        # tz = timezone('US/Central')
        # today = tz.localize(datetime.today())
        # patient_age = today.year - data.year - ((today.month, today.day) < (data.month, data.day))
        # if patient_age < 18:
        #    raise ValidationError(_('You must be 18 or over to use this service.'))

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

        if len(data) < 5:
            raise ValidationError(_('Invalid Zip code'))

        zip_code = data[0:5]
        if zip_code.isnumeric():
            zip_code = int(zip_code)
            if not ((75000 <= zip_code <= 79999) or (88500 <= zip_code <= 88599)):
                raise ValidationError(_('Invalid Zip code - we can only see patients in the state of Texas at this '
                                        'time.'))
        else:
            raise ValidationError(_('Invalid Zip code - Zip code must be numeric.'))

        if not data:
            raise ValidationError(_('Invalid Zip code - cannot be blank'))

        return data


class AffiliateForm(forms.Form):
    affiliate_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                           'placeholder': 'Affiliate Name*'}), max_length=200)
    affiliate_logo = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                           'placeholder': 'Logo static location*'}), max_length=200)
    affiliate_url = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                                    'placeholder': 'Base URL*'}),
                                      max_length=200)
    affiliate_price = forms.CharField(widget=forms.NumberInput(attrs={'class': "form-control form-control half-width",
                                                          'placeholder': 'Price in pennies*'}), max_length=20)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                           'placeholder': 'Coupon'}), max_length=200,
                           required=False
                           )


class PaymentForm(forms.Form):
    nonce = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control half-width",
                                                          'placeholder': 'nonce'}), max_length=2000, required=False)


class VitalsForm(forms.Form):
    height_feet = forms.FloatField(
        widget=forms.NumberInput(
            attrs={'required': True, 'type': 'number', 'style': 'width: 4em;', 'class': 'border'}
        )
    )
    height_inches = forms.FloatField(
        widget=forms.NumberInput(
            attrs={'required': True, 'type': 'number', 'style': 'width: 4em', 'class': 'border mt-2'}
        )
    )
    weight = forms.FloatField(
        widget=forms.NumberInput(
            attrs={'required': True, 'type': 'number', 'style': 'width: 6em', 'class': 'border'}
        )
    )


class SymptomsForm(forms.Form):
    allergies = forms.CharField(widget=forms.Textarea(
        attrs={
            "class": "overflow-auto border",
            "rows": "3", "cols": "40", "style": "width: 100%; resize: none; border: none"
        }))
    medications = forms.CharField(widget=forms.Textarea(
        attrs={
            "class": "overflow-auto border",
            "rows": "3", "cols": "40", "style": "width: 100%; resize: none; border: none"
        }))
    pancreatitis_thyroid_cancer = forms.BooleanField(
        widget=forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')]),
        required=True
    )
    previous_diagnosis = forms.MultipleChoiceField(
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={"onClick": "removeChecks(this)"}),
        choices=DIAGNOSED_CHOICES
    )

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

    def clean_pancreatitis_thyroid_cancer(self):
        data = self.cleaned_data['pancreatitis_thyroid_cancer']
        if data == 'no':
            return False
        return True


class PharmacyForm(forms.Form):
    pharmacy_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                                  'placeholder': 'Pharmacy Name*'}),
                                    max_length=200)
    pharmacy_address = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                                     'placeholder': 'Pharmacy Address*'}),
                                       max_length=2000)
    pharmacy_phone = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-control",
                                                                   'placeholder': 'Pharmacy Phone*'}), max_length=200)

    pharmacy_name.widget.attrs['readonly'] = True
    pharmacy_address.widget.attrs['readonly'] = True
    pharmacy_phone.widget.attrs['readonly'] = True


class ProviderForm(forms.Form):
    hpi = forms.CharField(widget=forms.Textarea(
        attrs={"class": "overflow-auto border smaller-field",
               "rows": "3", "cols": "40", "style": "width: 100%; resize: none; border: none"}),
        required=False)

    # Requires Redis server.
    assessments = forms.CharField(
        widget=forms.Select(
            choices=Icd10.objects.all().values_list('id', 'ICD10_DSC'),
            attrs={
                'class': 'form-control-sm select2',
                'placeholder': 'Assessment',
            }
        )
    )
    treatment = forms.CharField(widget=forms.Textarea(
        attrs={"class": "overflow-auto border smaller-field",
               "rows": "3", "cols": "40", "style": "width: 100%; resize: none; border: none"}),
        required=False)

    followup = forms.CharField(widget=forms.Textarea(
        attrs={"class": "overflow-auto border smaller-field",
               "rows": "3", "cols": "40", "style": "width: 100%; resize: none; border: none"}),
        required=False)

    return_to_work_notes = forms.CharField(widget=forms.Textarea(
        attrs={"class": "overflow-auto border smaller-field",
               "rows": "3", "cols": "40", "style": "width: 100%; resize: none; border: none"}),
        required=False)


class ICD10CodeLoad(forms.Form):
    file = forms.FileField()


class PrescriptionProvidedForm(forms.Form):
    prescription = forms.BooleanField(
        widget=forms.RadioSelect(choices=[('yes', 'Yes'), ('no', 'No')],),
        required=True
    )

    def clean_prescription(self):
        data = self.cleaned_data['prescription']
        if data == 'no':
            return False
        return True
